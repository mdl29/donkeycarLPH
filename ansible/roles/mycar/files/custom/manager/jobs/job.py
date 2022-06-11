import threading

import socketio
import logging
import traceback
from abc import abstractmethod
from threading import Thread
from typing import Dict, NoReturn, Optional

from ..schemas import Job as JobModel, JobState
from custom.manager.car_manager_api_service import CarManagerApiService


class Job(Thread):

    def __init__(self, parameters: Dict[str, any],
                 job_data: JobModel,
                 api: CarManagerApiService, sio: socketio.Client):
        """
        Init a job
        :param parameters: Job parameters (json parsed from API)
        :param job_data: Job entry.
        :param api: DonkeyCarManager API
        :param sio: SocketIO to manager
        """
        super(Job, self).__init__()
        self.daemon = True

        self.event_cancelled = threading.Event()  # Event set used to cancel the job
        self.parameters = parameters
        self.job_data: JobModel = job_data
        self.api = api
        self.sio = sio

        self.final_job_status = None
        self.final_job_error: Optional[Exception] = None
        self.final_job_fail_details: Optional[str] = None

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def get_id(self) -> int:
        """
        :return: The job ID
        """
        return self.job_data.job_id

    def cancel(self) -> NoReturn:
        """
        Will be called by job manager to cancel the job.
        """
        self.logger.info("Job[job_id: %i] request cancelling", self.get_id())
        self.event_cancelled.set()

    @abstractmethod
    def run_job(self):
        """Method called to run the job, it replace threading.run method to do error handling."""
        raise NotImplemented('You need to implement run_job for all jobs')

    def run(self) -> None:
        try:
            self.logger.info("Job[job_id: %i] of name '%s' starts running with parameters : %s", self.get_id(),
                              self.job_data.name, self.parameters)

            self.run_job()
            self.final_job_status = JobState.CANCELLED if self.event_cancelled.isSet() else JobState.SUCCEED

            self.logger.info("Job[job_id: %i] of name '%s' run SUCCESSFULLY ", self.get_id(), self.job_data.name)
        except Exception as e:
            self.final_job_status = JobState.FAILED
            self.final_job_error = e
            self.final_job_fail_details =\
                ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
            self.logger.error("Job[job_id: %i] failed with the following exception: %s", self.get_id(), e)
            self.logger.exception(e)

    @abstractmethod
    def run_threaded(self):
        """
        Part run threaded, is call with all donekcarmanacer I/O.
        Should be implemented if the job need some part I/O.
        Return outputs will be returned as donkeycarmanager part outputs.
        """
        pass