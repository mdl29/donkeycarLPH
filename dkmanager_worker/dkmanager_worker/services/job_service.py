import json
import logging
import threading
from typing import NoReturn, List, Optional, Iterable, Dict

import socketio

from dkmanager_worker.services.manager_api_service import ManagerApiService
from dkmanager_worker.services.jobs.generic_job import GenericJob as JobRun
from dkmanager_worker.models.schemas import JobState, Worker, Job as JobModel, EventJobChanged, WorkerState, JobCreate
# Match job name with job runnable instance
from ..helpers.RegistableEvents import RegistableEvent
from ..helpers.zeroconf import ServiceLocation

class JobService(threading.Thread):

    def __init__(self, api: ManagerApiService, ftp: ServiceLocation,
                 sio: socketio.Client, worker: Worker):
        """
        :param api: API manager instance.
        :param tub_path: Path where data are stored
        :param tub_writer: resetable thub writer
        :param sio: Socket IO client.
        :param worker: The current car worker.
        """
        super(JobService, self).__init__()
        self.daemon = True
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self._api = api
        self._ftp = ftp
        self._sio = sio
        self.worker = worker

        self.waiting_jobs_queue: List[JobModel] = []
        self.waiting_jobs_queue_changed = RegistableEvent()
        self.current_running_job: Optional[JobRun] = None

        event_jobs = f'jobs.{worker.worker_id}.updated'
        event_one_job = f'one_job.{worker.worker_id}.updated'
        sio.on(event_jobs, self.on_jobs_order_changed)
        self.logger.debug('Subscribed to event : %s', event_jobs)
        sio.on(f'one_job.{worker.worker_id}.updated', self.one_job_changed)
        self.logger.debug('Subscribed to event : %s', event_one_job)

    def one_job_changed(self, sio_message: Dict):
        """
        Event handler when a job for this worker as changed, might also be a new job assigned to this worker.
        :param sio_message: Socket IO message
        """
        self.logger.debug('on_job_changed')
        job_changed_event:EventJobChanged = EventJobChanged.parse_obj(sio_message)
        job = job_changed_event.job

        if job.state == JobState.WAITING:
            self.waiting_jobs_queue_changed.set()  # Tell we have new stuff
            return

        if job.state == JobState.PAUSING and self.current_running_job is not None:
            self.current_running_job.pause()

        if job.state == JobState.RESUMING and self.current_running_job is not None:
            self.current_running_job.resume()

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

    def set_worker_state(self, worker_state: WorkerState):
        """
        Update the current worker state.
        :param worker_state: state
        """
        self.worker.state = worker_state
        self._api.update_worker(worker=self.worker)

    def handle_next_job(self):
        current_job = self.current_running_job.job_data

        if current_job.next_job_details is None:
            return

        next_job_details = {}
        try:
            next_job_details = json.loads(current_job.next_job_details)
        except Exception as e:
            self.logger.error('Parsing json next_job_details for job_id: %s, FAILED with the following exception :')
            self.logger.exception(e)
            return

        default_job_parameters = {
            'worker_id': current_job.worker_id,
            'worker_type': current_job.worker_type,
            'player_id': current_job.player_id,
            'state': JobState.WAITING
        }
        next_job_dict = { **default_job_parameters, **next_job_details }
        next_job = JobCreate( **next_job_dict )
        self.logger.debug('Creating next job, next_job.name: %s', next_job.name)
        next_job = self._api.create_job(next_job)
        # Job as to be run just after the current job
        self.logger.debug('Moving next job (%i), just after current job (%i)', next_job.job_id, current_job.job_id)
        next_job = self._api.job_move_after(next_job.job_id, after_job_id=current_job.job_id)
        self.logger.debug('Next job as rank %i an current job as rank %i', next_job.rank, current_job.rank)

    def parse_job_parameters(self, job_parameters: str) -> Dict:
        """
        Parse job parameters
        :param job_parameters: JSON encoded parameters
        :return: A dict of parsed parameters
        """
        parameters = {}
        try:
            parameters = json.loads(job_parameters)
        except Exception as e:
            self.logger.error('Parsing json parameters for job_id: %s, FAILED with the following exception :')
            self.logger.exception(e)

        return parameters

    def run(self):
        for job in self.next_job():
            self.set_worker_state(WorkerState.BUSY)
            job_run = self.init_job_run(job)
            self.current_running_job = job_run

            self.on_before_new_job_start()

            # Start the job
            job_run.start()

            # Job ended
            job_run.join()

            job.state = job_run.final_job_status
            if job.state == JobState.FAILED and job_run.final_job_fail_details is not None:
                job.fail_details = job_run.final_job_fail_details

            # Handle next job
            self.handle_next_job()

            self._api.update_job(job)

            self.on_current_job_ends()

            # Delete and unset the current job
            del self.current_running_job
            self.current_running_job = None

            self.set_worker_state(WorkerState.AVAILABLE)

    def on_before_new_job_start(self) -> NoReturn:
        """
        Executed when a new job is selected for a run.
        At this stage current_running_job is already setted with the new job
        """
        pass

    def on_current_job_ends(self) -> NoReturn:
        """
        Executed when the current job execution as finished, final state is setted.
        Should be overridden. Worker is set AVAILABLE just after it.
        """
        pass
