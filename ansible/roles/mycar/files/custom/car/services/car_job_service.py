from datetime import datetime
from typing import NoReturn, Optional, Dict, Type, Tuple

import socketio

from dkmanager_worker.services.manager_api_service import ManagerApiService
from dkmanager_worker.services.job_service import JobService
from custom.car.services.jobs.job import Job as JobRun
from custom.car.services.jobs.job_drive import JobDrive
from custom.car.services.jobs.job_record import JobRecord
from dkmanager_worker.models.schemas import Worker, Job as JobModel, Car
# Match job name with job runnable instance
from dkmanager_worker.helpers.zeroconf import ServiceLocation
from custom.car.parts.custom_tub_writer import CustomTubWriter

JOB_NAME_TO_JOB_RUNNABLE: Dict[str, Type[JobRun]] = {
    'DRIVE': JobDrive,
    'RECORD': JobRecord
}

class CarJobService(JobService):

    def __init__(self, api: ManagerApiService, ftp: ServiceLocation,
                 tub_path: str, tub_writer: CustomTubWriter,
                 sio: socketio.Client, worker: Worker, car: Car):
        """
        :param api: API manager instance.
        :param tub_path: Path where data are stored
        :param tub_writer: resetable thub writer
        :param sio: Socket IO client.
        :param worker: The current car worker.
        """
        super(CarJobService, self).__init__(api=api, ftp=ftp,
                                            sio=sio, worker=worker)

        self._tub_path = tub_path
        self._tub_writer = tub_writer

        self.car = car

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

        parameters = self.parse_job_parameters(job.parameters)

        job_run_instance = job_run_class(
            parameters=parameters, job_data=job,
            api=self._api, ftp=self._ftp, sio=self._sio,
            tub_path=self._tub_path, tub_writer=self._tub_writer,
            car=self.car)
        return job_run_instance

    def on_before_new_job_start(self) -> NoReturn:
        """
        Executed when a new job is selected for a run.
        At this stage current_running_job is already setted with the new job
        """
        super(CarJobService, self).on_before_new_job_start()

        # Handeling car state
        self.car.current_player_id = self.current_running_job.job_data.player_id
        self.car.current_stage = self.current_running_job.job_data.name
        self.car.current_race_id = None
        self._api.update_car(self.car)

    def on_current_job_ends(self) -> NoReturn:
        """
        Executed when the current job execution as finished, final state is setted.
        Should be overridden. Worker is set AVAILABLE just after it.
        """
        # Handeling car state
        self.car.current_player_id = None
        self.car.current_stage = None
        self.car.current_race_id = None
        self._api.update_car(self.car)

    def run_threaded_current_job(self,
                                 user_throttle: None,
                                 laptimer_current_start_lap_datetime: Optional[datetime] = None,
                                 laptimer_current_lap_duration: Optional[int] = None,
                                 laptimer_last_lap_start_datetime: Optional[datetime] = None,
                                 laptimer_last_lap_duration: Optional[int] = None,
                                 laptimer_last_lap_end_date_time: Optional[datetime] = None,
                                 laptimer_laps_total: Optional[int] = None,
                                 controller_x_pressed: Optional[bool] = False) -> Tuple[float, str, bool, bool]:
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
                laptimer_laps_total,
                controller_x_pressed
            )
            return res

        # Default values
        user_throttle = 0.0
        job_name = 'NO_JOB'
        laptimer_reset_all = True
        recording_state = False
        return user_throttle, job_name, laptimer_reset_all, recording_state
