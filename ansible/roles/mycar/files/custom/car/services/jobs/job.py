import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

import socketio

from custom.car.parts.custom_tub_writer import CustomTubWriter
from custom.generic_worker.helpers.RegistableEvents import RegistableEvent
from custom.generic_worker.helpers.zeroconf import ServiceLocation
from custom.generic_worker.models.schemas import Job as JobModel, Car
from custom.generic_worker.services.jobs.generic_job import GenericJob
from custom.generic_worker.services.manager_api_service import ManagerApiService


class Job(GenericJob):

    def __init__(self, parameters: Dict[str, any],
                 job_data: JobModel, car: Car,
                 api: ManagerApiService, ftp: ServiceLocation,
                 sio: socketio.Client,
                 tub_path: str, tub_writer: CustomTubWriter):
        """
        Init a job
        :param parameters: Job parameters (json parsed from API)
        :param job_data: Job entry.
        :param api: DonkeyCarManager API
        :param ftp: DonkeyCarManager FTP server location details
        :param sio: SocketIO to manager
        :param tub_path: Path where data are stored
        :param tub_writer: resetable tub writer part
        """
        super(Job, self).__init__(parameters=parameters,
                 job_data=job_data,
                 api=api, ftp=ftp,
                 sio=sio)

        self.car = car
        self.tub_path = tub_path
        self.tub_writer = tub_writer

        # Controllers event
        self.event_controller_x_pressed = RegistableEvent()  # "X" button was pressed on the controller

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def run_threaded(self,
                     user_throttle: None,
                     laptimer_current_start_lap_datetime: Optional[datetime] = None,
                     laptimer_current_lap_duration: Optional[int] = None,
                     laptimer_last_lap_start_datetime: Optional[datetime] = None,
                     laptimer_last_lap_duration: Optional[int] = None,
                     laptimer_last_lap_end_date_time: Optional[datetime] = None,
                     laptimer_laps_total: Optional[int] = None,
                     controller_x_pressed: Optional[bool] = False) -> Tuple[float, str, bool, bool]:
        """
        Part run threaded, is call with all donekcarmanacer I/O.
        Should be implemented if the job need some part I/O.
        Return outputs will be returned as donkeycarmanager part outputs.
        """

        if controller_x_pressed:
            self.logger.debug('Controller X button was pressed, trigger event')
            self.event_controller_x_pressed.set()
