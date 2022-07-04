import logging
from typing import Optional, NoReturn

import socketio

from dkmanager_worker.services.manager_api_service import ManagerApiService
from dkmanager_worker.services.job_service import JobService
from dkmanager_worker.models.schemas import Worker, WorkerState
from dkmanager_worker.services.heartbeat_service import HeartBeatService
from dkmanager_worker.helpers.zeroconf import find_zero_conf_service, ServiceLocation

RES_WORKERS = "workers"
ZERO_CONF_API_TYPE = "_http._tcp.local."
ZERO_CONF_FTP_TYPE = "_ftp._tcp.local."
ZERO_CONF_NAME = "donkeycarmanager"
ZERO_CONF_MAX_TRY = 15  # Will try 15 times to find server IP


class ManagerNoApiFoundException(Exception):
    pass


class WorkerService:
    def __init__(self,
                 api_origin: Optional[str] = None,
                 ftp_location: Optional[ServiceLocation] = None):
        """
        :param api_origin:  Optionnal api path, if not given will use zeroconf to find it and use the first found IP.
            Eg:
        :param network_interface: Network interface used to determine the car's IP addr.
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self._api_origin = api_origin if api_origin else self._find_api_with_zero_conf()
        self._api = ManagerApiService(self._api_origin)

        self._ftp = ftp_location if ftp_location else self._find_ftp_with_zero_conf()

        self._sio = socketio.Client()
        self._sio.connect(self._api_origin, socketio_path='/ws/socket.io')

    def start_services(self):
        """
        Starts all worker needed services (heartbeat, job_manager ..)
        """


        # Cleaning all past pending job (running, pausing, paused, cancelling ..)
        nb_cleaned_jobs = self._api.worker_clean(self.worker, 'Car restarted')
        self.logger.debug(
            'Cleaned/failled : %i jobs that were in strange state, with "Car restarted" reason', nb_cleaned_jobs)

        # Worker heart beat, keep it alive and set it's state to available until job is taken
        self._worker_heartbeat = HeartBeatService(api_origin=self._api_origin, worker=self.worker)
        self._worker_heartbeat.start()

        # Job managment
        self._job_manager.start()

    def set_job_manager(self, job_manager: JobService) -> NoReturn:
        """
        Define the current worker job manager/service
        :param job_manager:
        """
        self._job_manager = job_manager

    def set_worker(self, worker: Worker) -> NoReturn:
        """
        set current worker worker
        :param worker:
        """
        self.worker = worker

    @staticmethod
    def _find_ftp_with_zero_conf() -> ServiceLocation:
        """
        Find API URL using zero conf.
        :return: The API URL
        """
        logger = logging.getLogger(WorkerService.__module__ + "." + WorkerService.__class__.__name__)
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
        logger = logging.getLogger(WorkerService.__module__ + "." + WorkerService.__class__.__name__)
        logger.debug('Searching API using zeroconf ...')
        api_info = find_zero_conf_service(ZERO_CONF_API_TYPE, ZERO_CONF_NAME)

        if api_info is not None:
            url = f"http://{api_info.ip}:{api_info.port}"
            logger.debug('Found manager API at : %s', url)
            return url

        raise ManagerNoApiFoundException("Can't find the API using zero conf")

    def update_worker_state(self, state: WorkerState) -> NoReturn:
        """
        Update current car state.
        :param state: Current state
        """
        self.worker.state = state
        self._api.update_worker(self.worker)
