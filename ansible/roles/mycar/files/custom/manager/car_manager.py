import logging
from datetime import datetime
from typing import Optional, NoReturn, List, Tuple

import socketio
import socket
import os
from netifaces import ifaddresses, AF_INET

from .car_manager_api_service import CarManagerApiService
from .job_manager import JobManager
from .schemas import Car, Worker, WorkerCreate, WorkerState, WorkerType, CarCreate
from .worker_heartbeat import WorkerHeartBeat
from ..helpers.zeroconf import find_zero_conf_service, ZeroConfResult

RES_WORKERS = "workers"
RES_CARS = "cars"
ZERO_CONF_API_TYPE = "_http._tcp.local."
ZERO_CONF_FTP_TYPE = "_ftp._tcp.local."
ZERO_CONF_NAME = "donkeycarmanager"
ZERO_CONF_MAX_TRY = 15  # Will try 15 times to find server IP


class ManagerNoApiFoundException(Exception):
    pass


class CarManager:
    def __init__(self,
                 tub_path: str,
                 api_origin: Optional[str] = None,
                 network_interface: str = "wlan0"):
        """
        :param tub_path: Path where data are stored
        :param api_origin:  Optionnal api path, if not given will use zeroconf to find it and use the first found IP.
            Eg:
        :param network_interface: Network interface used to determine the car's IP addr.
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self._api_origin = api_origin if api_origin else self._find_api_with_zero_conf()
        self._api = CarManagerApiService(self._api_origin)

        self._ftp = self._find_ftp_with_zero_conf()

        self._sio = socketio.Client()
        self._sio.connect(self._api_origin, socketio_path='/ws/socket.io')

        self._network_interface = network_interface  # Used to find IP addr
        self.worker: Optional[Worker] = None  # Worker associated to this car
        self.car: Car = self._update_or_create_car()  # Car representation of the current car

        if self.worker is None:
            raise Exception("No worker created for this car")

        # Cleaning all past pending job (running, pausing, paused, cancelling ..)
        nb_cleaned_jobs = self._api.worker_clean(self.worker, 'Car restarted')
        self.logger.debug(
            'Cleaned/failled : %i jobs that were in strange state, with "Car restarted" reason', nb_cleaned_jobs)

        # Worker heart beat, keep it alive and set it's state to available until job is taken
        self._worker_heartbeat = WorkerHeartBeat(api_origin=self._api_origin, worker=self.worker)
        self._worker_heartbeat.start()

        # Job managment
        self._job_manager = JobManager(self._api, self._ftp, tub_path, self._sio, self.worker, self.car)
        self._job_manager.start()

    @staticmethod
    def _find_ftp_with_zero_conf() -> ZeroConfResult:
        """
        Find API URL using zero conf.
        :return: The API URL
        """
        logger = logging.getLogger(CarManager.__module__ + "." + CarManager.__class__.__name__)
        logger.debug('Searching API using zeroconf ...')
        ftp_info = find_zero_conf_service(ZERO_CONF_FTP_TYPE, ZERO_CONF_NAME)

        if ftp_info is not None:
            return ftp_info

        raise ManagerNoApiFoundException("Can't find the FTP using zero conf")

    @staticmethod
    def _find_api_with_zero_conf() -> str:
        """
        Find API URL using zero conf.
        :return: The API URL
        """
        logger = logging.getLogger(CarManager.__module__ + "." + CarManager.__class__.__name__)
        logger.debug('Searching API using zeroconf ...')
        api_info = find_zero_conf_service(ZERO_CONF_API_TYPE, ZERO_CONF_NAME)

        if api_info is not None:
            url = f"http://{api_info.ip}:{api_info.port}"
            logger.debug('Found manager API at : %s', url)
            return url

        raise ManagerNoApiFoundException("Can't find the API using zero conf")

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
                          'color': os.environ.get('CONTROLLER_LED_COLOR')}

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
                     laptimer_laps_total: Optional[int]=None
                     ) -> Tuple[float, str, bool, bool]:
        """
        :param user_throttle: User throttle value
        :return: [manager/enable_controller_throttle, ..]
            user/throttle
            manager/job_name
            laptimer/reset_all
            recording
        """
        res = self._job_manager.run_threaded_current_job(
            user_throttle,
            laptimer_current_start_lap_datetime,
            laptimer_current_lap_duration,
            laptimer_last_lap_start_datetime,
            laptimer_last_lap_duration,
            laptimer_last_lap_end_date_time,
            laptimer_laps_total
        )
        return res

    def run(self):
        return self.run_threaded()
