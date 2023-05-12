import os
import logging
from pathlib import Path
from typing import Optional

from dkmanager_worker.helpers.zeroconf import ServiceLocation
from pydantic import BaseModel

from dkmanager_trainer.services.ia_job_service import IaJobService
from dkmanager_worker.models.schemas import WorkerType, WorkerCreate, WorkerState, Worker
from dkmanager_worker.services.worker_service import WorkerService

# Configuration file of the current AI Worker
# HOME_FOLDER/donkey_car_lph_ai_worker_config.json
WORKER_CONFIG_LOCATION = f"{os.path.expanduser('~')}/donkey_car_lph_ai_worker_config.json"


class AIWorkerConfig(BaseModel):
    """
        Format of the configuration file of the worker, located in WORKER_CONFIG_LOCATION
    """
    worker_id: int


class AiTrainerWorkerService(WorkerService):

    def __init__(self, api_origin: Optional[str] = None,
                 ftp_location: Optional[ServiceLocation] = None):
        """
        :param api_origin:  Location of the donkeycar manager API.
        :param ftp_location: Location of the FTP server.
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        super(AiTrainerWorkerService, self).__init__(
            api_origin=api_origin,
            ftp_location=ftp_location)

        self.worker = self.create_or_get_worker()
        if self.worker is None:
            raise Exception("No worker created for this car")

        self.set_worker(worker=self.worker)

        # Job management
        job_manager = IaJobService(self._api, self._ftp, self._sio, self.worker)
        self.set_job_manager(job_manager)

        self.start_services()

    @staticmethod
    def get_ai_worker_config() -> AIWorkerConfig:
        """
        :return: Current AI Worker configuration.
        """
        if Path(WORKER_CONFIG_LOCATION).exists():
            return AIWorkerConfig.parse_file(WORKER_CONFIG_LOCATION)

        return None

    def create_ai_worker(self) -> Worker:
        """
        Create the AI Worker
        :return: The newly created AI Worker
        """
        worker_create_request = WorkerCreate(type=WorkerType.AI_TRAINER, state=WorkerState.STOPPED)
        worker = self._api.create_worker(worker_create_request)

        # Save worker AI as configuration file
        self.logger.info('Saving newly created worker id %i, for this AI Trainner in %s',
                         worker.worker_id,
                         WORKER_CONFIG_LOCATION)
        Path(WORKER_CONFIG_LOCATION).write_text(AIWorkerConfig(worker_id=worker.worker_id).json())

        return worker

    def create_or_get_worker(self) -> Worker:
        """
        Create IA worker if needed.
        """
        worker = None

        ai_worker_config = AiTrainerWorkerService.get_ai_worker_config()
        if ai_worker_config is not None:
            worker = self._api.get_worker(ai_worker_config.worker_id)

        if worker is not None:  # Worker fetched, already existing using it
            self.logger.debug('Using existing IA Worker with ID : %i', worker.worker_id)
            return worker
        else:
            self.logger.debug('No existing AI worker, creating one')
            return self.create_ai_worker()
