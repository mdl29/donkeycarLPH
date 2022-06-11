import threading
from typing import NoReturn, List, Optional, Iterable, Dict, Type

import socketio
import json
import logging

from custom.manager.car_manager_api_service import CarManagerApiService
from .jobs.job_drive import JobDrive
from .schemas import JobState, Worker, Job as JobModel, EventJobChanged, EventJobQueue
from .jobs.job import Job as JobRun

# Match job name with job runnable instance
JOB_NAME_TO_JOB_RUNNABLE: Dict[str, Type[JobRun]] = {
    'DRIVE': JobDrive
}

class JobManager(threading.Thread):

    def __init__(self, api: CarManagerApiService, sio: socketio.Client, worker: Worker):
        """
        :param api: API manager instance.
        :param sio: Socket IO client.
        :param worker: The current car worker.
        """
        super(JobManager, self).__init__()
        self.daemon = True
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self._api = api
        self._sio = sio
        self.worker = worker
        self.waiting_jobs_queue: List[JobModel] = []
        self.waiting_jobs_queue_changed = threading.Event()
        self.current_running_job: Optional[JobRun] = None

        event_jobs = f'jobs.{worker.worker_id}.updated'
        event_one_job = f'one_job.{worker.worker_id}.updated'
        sio.on(event_jobs, self.on_jobs_order_changed)
        self.logger.debug('Subscribed to event : %s', event_jobs)
        sio.on(f'one_job.{worker.worker_id}.updated', self.one_job_changed)
        self.logger.debug('Subscribed to event : %s', event_one_job)

    def one_job_changed(self, sio_message: Dict):
        """
        Event handler when a job for this worker as changed.
        :param sio_message: Socket IO message
        """
        self.logger.debug('on_job_changed')
        job_changed_event:EventJobChanged = EventJobChanged.parse_obj(sio_message)
        job = job_changed_event.job

        # Not a cancelation, we have nothing to do
        # Qeued job parameter change, on_jobs_order_changed will refresh it
        if job.state != JobState.CANCELLING:
            return

        if self.current_running_job is not None and job.job_id == self.current_running_job.get_id():
            self.current_running_job.cancel()  # Telling him we want to stop
        else:
            # Backend want to cancel non running job, updating them as cancelled as they are not running
            job.state = JobState.CANCELLED
            self._api.update_job(job)

    def on_jobs_order_changed(self, sio_message: Dict):
        """
        Event handler for queued job changes
        :param sio_message: event message with all job, should be a json of EventJobQueue format
        """
        self.logger.debug('on_jobs_changed')
        # We aren't using data from the event, as they might be from an outdated event if we receive several updates
        # at the same time, so we choose to only set a flag and fetch the data at the right time
        self.waiting_jobs_queue_changed.set() # Tell we have new stuff

    def fetch_waiting_jobs(self) -> NoReturn:
        """
        Fetch / refresh waiting jobs from the API.
        """
        self.waiting_jobs_queue = self._api.get_jobs(self.worker, JobState.WAITING)
        self.logger.debug("Fetched %i waiting jobs for current worker", len(self.waiting_jobs_queue))

    def next_job(self) -> Iterable[JobModel]:
        """
        Infinite iterator, return next job to be run.
        :return: iterator of jobs
        """
        while True:
            self.logger.debug("Worker request a new job ...")
            # Pull for new jobs, always it's the simplest way
            self.fetch_waiting_jobs()
            self.waiting_jobs_queue_changed.clear()  # We just refreshed

            if len(self.waiting_jobs_queue) == 0: # Still no jobs after fetch, going to wait
                self.logger.debug("No waiting job, going to wait for jobs events")
                self.waiting_jobs_queue_changed.wait()
                continue
            else:
                job = self.waiting_jobs_queue.pop(0)
                self.logger.debug("Job to be run is job_id: %i, job_name: %s", job.job_id, job.name)
                yield job

    def init_job_run(self, job: JobModel) -> JobRun:
        """
        Return job instance form job definition.
        :param job: Job definition
        :return: A runnable / job thread to be started
        """
        job_run_class = JOB_NAME_TO_JOB_RUNNABLE.get(job.name)

        if job_run_class is None:
            #TODO display log error
            # Throw an error
            return None

        parameters = {}
        try:
            parameters = json.loads(job.parameters)
        except Exception as e:
            self.logger.error('Parsing json parameters for job_id: %s, FAILED with the following exception :')
            self.logger.exception(e)

        job_run_instance = job_run_class(parameters=parameters, job_data=job, api=self._api, sio=self._sio)
        return job_run_instance

    def run(self):
        for job in self.next_job():
            job_run = self.init_job_run(job)
            self.current_running_job = job_run

            # Start the job
            job_run.start()
            job.state = JobState.RUNNING
            self._api.update_job(job)

            # Job ended
            job_run.join()

            job.state = job_run.final_job_status
            if job.state == JobState.FAILED and job_run.final_job_fail_details is not None:
                job.fail_details = job_run.final_job_fail_details

            self._api.update_job(job)
            self.current_running_job = None

    def run_threaded_current_job(self, user_throttle: None):
        """
        See donkeycar CarManager part for details.
        """

        if self.current_running_job is not None:
            return self.current_running_job.run_threaded(user_throttle)


        return 0.0, 'NO_JOB'
