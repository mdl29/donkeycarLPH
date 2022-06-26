import threading
from datetime import datetime
from typing import NoReturn, List, Optional, Iterable, Dict, Type, Tuple

import socketio
import json
import logging

from custom.manager.car_manager_api_service import CarManagerApiService
from .jobs.job_drive import JobDrive
from .jobs.job_record import JobRecord
from .schemas import JobState, Worker, Job as JobModel, EventJobChanged, WorkerState, Car, JobCreate
from .jobs.job import Job as JobRun

# Match job name with job runnable instance
from ..helpers.RegistableEvents import RegistableEvent
from ..helpers.zeroconf import ZeroConfResult

JOB_NAME_TO_JOB_RUNNABLE: Dict[str, Type[JobRun]] = {
    'DRIVE': JobDrive,
    'RECORD': JobRecord
}

class JobManager(threading.Thread):

    def __init__(self, api: CarManagerApiService, ftp: ZeroConfResult, tub_path: str, sio: socketio.Client, worker: Worker, car: Car):
        """
        :param api: API manager instance.
        :param tub_path: Path where data are stored
        :param sio: Socket IO client.
        :param worker: The current car worker.
        """
        super(JobManager, self).__init__()
        self.daemon = True
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self._api = api
        self._ftp = ftp
        self._sio = sio
        self._tub_path = tub_path
        self.worker = worker
        self.car = car

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

        job_run_instance = job_run_class(
            parameters=parameters, job_data=job,
            api=self._api, ftp=self._ftp, sio=self._sio, tub_path=self._tub_path,
            car=self.car)
        return job_run_instance

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

    def run(self):
        for job in self.next_job():
            self.set_worker_state(WorkerState.BUSY)
            job_run = self.init_job_run(job)
            self.current_running_job = job_run

            # Handeling car state
            self.car.current_player_id = job.player_id
            self.car.current_stage = job.name
            self.car.current_race_id = None
            self._api.update_car(self.car)

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

            # Handeling car state
            self.car.current_player_id = None
            self.car.current_stage = None
            self.car.current_race_id = None
            self._api.update_car(self.car)

            self.set_worker_state(WorkerState.AVAILABLE)

    def run_threaded_current_job(self,
                                 user_throttle: None,
                                 laptimer_current_start_lap_datetime: Optional[datetime] = None,
                                 laptimer_current_lap_duration: Optional[int] = None,
                                 laptimer_last_lap_start_datetime: Optional[datetime] = None,
                                 laptimer_last_lap_duration: Optional[int] = None,
                                 laptimer_last_lap_end_date_time: Optional[datetime] = None,
                                 laptimer_laps_total: Optional[int] = None) -> Tuple[float, str, bool, bool]:
        """
        See donkeycar CarManager part for details.
        """

        if self.current_running_job is not None:
            res = self.current_running_job.run_threaded(
                user_throttle,
                laptimer_current_start_lap_datetime,
                laptimer_current_lap_duration,
                laptimer_last_lap_start_datetime,
                laptimer_last_lap_duration,
                laptimer_last_lap_end_date_time,
                laptimer_laps_total
            )
            return res

        # Default values
        user_throttle = 0.0
        job_name = 'NO_JOB'
        laptimer_reset_all = True
        recording_state = False
        return user_throttle, job_name, laptimer_reset_all, recording_state
