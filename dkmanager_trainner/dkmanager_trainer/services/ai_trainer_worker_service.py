import logging
from typing import Optional

from dkmanager_worker.helpers.zeroconf import ServiceLocation

from dkmanager_trainer.services.ia_job_service import IaJobService
from dkmanager_worker.models.schemas import WorkerType, WorkerCreate, WorkerState, Worker
from dkmanager_worker.services.worker_service import WorkerService


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

    def create_or_get_worker(self) -> Worker:
        """
        Create IA worker if needed.
        """
        ai_workers = self._api.get_workers(worker_type=WorkerType.AI_TRAINER)

        if len(ai_workers) > 0: # We assume there is only one IA Worker at all
            worker = ai_workers[0]
            self.logger.debug('Using existing IA Worker with ID : %i', worker.worker_id)
            return worker
        else:
            self.logger.debug('No existing AI worker, creating one')
            worker = WorkerCreate(type=WorkerType.AI_TRAINER, state=WorkerState.STOPPED)
            return self._api.create_worker(worker)
