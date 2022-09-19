from datetime import datetime

import socketio
import logging
import traceback
from abc import abstractmethod
from threading import Thread
from typing import Dict, NoReturn, Optional

from dkmanager_worker.models.schemas import Job as JobModel, JobState
from dkmanager_worker.services.manager_api_service import ManagerApiService
from dkmanager_worker.helpers.conditional_events import ConditionalEvents, CondEventsOperator
from dkmanager_worker.helpers.RegistableEvents import RegistableEvent
from dkmanager_worker.helpers.zeroconf import ServiceLocation


class GenericJob(Thread):
    def __init__(self, parameters: Dict[str, any],
                 job_data: JobModel,
                 api: ManagerApiService, ftp: ServiceLocation,
                 sio: socketio.Client):
        """
        Init a job
        :param parameters: Job parameters (json parsed from API)
        :param job_data: Job entry.
        :param api: DonkeyCarManager API
        :param ftp: DonkeyCarManager FTP server location details
        :param sio: SocketIO to manager
        """
        super(GenericJob, self).__init__()
        self.daemon = True

        self.event_cancelled = RegistableEvent()  # Event set used to cancel the job
        self.event_paused = RegistableEvent()  # Event set used to pause the job
        self.event_resume = RegistableEvent()  # Event set used to resume the job

        self.parameters = parameters
        self.job_data: JobModel = job_data
        self.api = api
        self.ftp = ftp
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

    def pause(self) -> NoReturn:
        """
        Will be called by job manager to pause the job.
        """
        self.logger.info("Job[job_id: %i] request pausing", self.get_id())
        self.event_paused.set()

    def resume(self) -> NoReturn:
        """
        Will resume a paused job.
        """
        self.event_resume.set()

    @abstractmethod
    def run_job(self, resumed=False):
        """
        :param resumed: True if the run_job was already done and it's juste a resuming.
        """
        raise NotImplemented('You need to implement run_job for all jobs')

    def display_screen_msg(self, msg):
        """
        :param msg: Message to be displayed on the screen.
        """
        self.job_data.screen_msg = msg
        self.job_data.screen_msg_display = True
        self.api.update_job(self.job_data)
        self.logger.debug('[job_id: %i]  Displaying message on screen : %s',
                          self.get_id(), msg)

    def hidde_screen_msg(self):
        """
        Hidden the message on the screen.
        """
        self.job_data.screen_msg = None
        self.job_data.screen_msg_display = False
        self.api.update_job(self.job_data)

    def run(self) -> None:
        was_resumed = False
        with ConditionalEvents([self.event_resume, self.event_cancelled], CondEventsOperator.OR) as resumed_or_cancelled:
            try:
                self.logger.info("Job[job_id: %i] of name '%s' starts running with parameters : %s", self.get_id(),
                                  self.job_data.name, self.parameters)

                while True: # could be infinite resuming
                    self.logger.info("Job[job_id: %i] of name '%s' is run (was_resumed=%r)",
                                     self.get_id(), self.job_data.name, was_resumed)

                    self.job_data.state = JobState.RUNNING
                    self.api.update_job(self.job_data)
                    self.run_job(resumed=was_resumed)

                    # Was cancelled we quit
                    if self.event_cancelled.isSet():
                        self.final_job_status = JobState.CANCELLED
                        self.logger.info("Job[job_id: %i] of name '%s' was cancelled ",
                                         self.get_id(), self.job_data.name)
                        return

                    # Is paused
                    if self.event_paused.isSet():
                        # Updating state to paused
                        self.job_data.state = JobState.PAUSED
                        self.api.update_job(job=self.job_data)
                        self.logger.info("Job[job_id: %i] of name '%s' is paused",
                                         self.get_id(), self.job_data.name)

                        # Wait for resuming or cancelled
                        resumed_or_cancelled.wait()

                        # Was cancelled during pause
                        if self.event_cancelled.isSet():
                            self.final_job_status = JobState.CANCELLED
                            self.logger.info("Job[job_id: %i] of name '%s' was cancelled ",
                                             self.get_id(), self.job_data.name)
                            return
                        else: # Was resumed
                            was_resumed = True
                            self.event_paused.clear() # Unset pause as it's resumed
                            self.logger.info("Job[job_id: %i] of name '%s' was resumed",
                                             self.get_id(), self.job_data.name)
                            continue # We can go on and on ... 🔄
                    else:
                        self.final_job_status = JobState.SUCCEED
                        self.logger.info("Job[job_id: %i] of name '%s' run ended with status %s ",
                                         self.get_id(), self.job_data.name, self.final_job_status)
                        return
            except Exception as e:
                self.final_job_status = JobState.FAILED
                self.final_job_error = e
                self.final_job_fail_details =\
                    ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
                self.logger.error("Job[job_id: %i] failed with the following exception: %s", self.get_id(), e)
                self.logger.exception(e)
