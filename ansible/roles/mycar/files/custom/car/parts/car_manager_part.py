import logging
import os
import socket
from datetime import datetime
from typing import Optional, NoReturn, List, Tuple, Callable

from dkmanager_worker.helpers.zeroconf import ServiceLocation
from dkmanager_worker.models.schemas import Car, WorkerCreate, WorkerState, WorkerType, CarCreate
from dkmanager_worker.services.worker_service import WorkerService
from netifaces import ifaddresses, AF_INET

from custom.car.parts.custom_tub_writer import CustomTubWriter
from custom.car.services.car_job_service import CarJobService

RES_CARS = "cars"


class ManagerNoApiFoundException(Exception):
    pass


class CarManagerPart(WorkerService):
    def __init__(self,
                 tub_path: str,
                 tub_writer: CustomTubWriter,
                 api_origin: Optional[str] = None,
                 ftp_location: Optional[ServiceLocation] = None,
                 network_interface: str = "wlan0"):
        """
        :param tub_path: Path where data are stored
        :param tub_writer: Resetable thumb writer
        :param api_origin:  Optionnal api path, if not given will use zeroconf to find it and use the first found IP.
            Eg:
        :param network_interface: Network interface used to determine the car's IP addr.
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        super(CarManagerPart, self).__init__(
            api_origin=api_origin,
            ftp_location=ftp_location)

        # Create car and worker
        self._network_interface = network_interface
        self.car: Car = self._update_or_create_car()  # Car representation of the current car

        if self.worker is None:
            raise Exception("No worker created for this car")

        self.set_worker(worker=self.worker)

        # Job managment
        job_manager = CarJobService(self._api, self._ftp, tub_path, tub_writer, self._sio, self.worker, self.car)
        self.set_job_manager(job_manager)

        self.start_services()

    @staticmethod
    def get_car_name() -> str:
        """
        :return: Current car name.
        """
        return socket.gethostname()

    def _update_or_create_car(self) -> Car:
        """
        Create car matching the name or update it, as car always have a worker associated it will also create the worker.
        :return:
        """
        car_name = self.get_car_name()
        current_car_basic_details = { 'name': car_name,
                          'ip': ifaddresses(self._network_interface)[AF_INET][0]['addr'],
                          'color': os.environ.get('CONTROLLER_LED_COLOR'),
                          'inverted_controls': False,
                          'throttle_scale': 0.5}

        existing_car = self._api.get_car(car_name)
        if existing_car is not None:  # Need to update the car with current details
            api_car_refreshed = Car.parse_obj({**existing_car.dict(), **current_car_basic_details})  # Override API car props to update them
            self.worker = api_car_refreshed.worker

            return self._api.update_car(api_car_refreshed)
        else:  # No existing car, so no worker need to create one also
            worker_create = WorkerCreate(type=WorkerType.CAR, state=WorkerState.STOPPED)
            self.worker = self._api.create_worker(worker_create)

            car = CarCreate(**current_car_basic_details, worker_id=self.worker.worker_id)
            return self._api.create_car(car)

    def update_worker_state(self, state: WorkerState) -> NoReturn:
        """
        Update current car state.
        :param state: Current state
        """
        self.worker.state = state
        self._api.update_worker(self.worker)

    def update(self):
        return

    def run_threaded(self,
                     user_throttle=None,
                     laptimer_current_start_lap_datetime: Optional[datetime] = None,
                     laptimer_current_lap_duration: Optional[int] = None,
                     laptimer_last_lap_start_datetime: Optional[datetime]=None,
                     laptimer_last_lap_duration: Optional[int] = None,
                     laptimer_last_lap_end_date_time: Optional[datetime] = None,
                     laptimer_laps_total: Optional[int]=None,
                     controller_x_pressed: Optional[bool]=False,
                     inverted: Optional[bool]=False,
                     scale: Optional[float]=0.5,
                     ) -> Tuple[float, str, bool, bool]:
        """
        :param user_throttle: User throttle value
        :return: [manager/enable_controller_throttle, ..]
            user/throttle
            manager/job_name
            laptimer/reset_all
            recording
        """
        changed = False
        if inverted != self.car.inverted_controls:
            self.logger.info("Controls inverted")
            self.car.inverted_controls = inverted
            changed = True
        if scale != self.car.throttle_scale:
            self.car.throttle_scale = scale
            changed = True
        if changed:
            self._api.update_car(self.car)

        res = self._job_manager.run_threaded_current_job(
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

    def run(self):
        return self.run_threaded()
