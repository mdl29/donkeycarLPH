import logging
import threading
import time

from custom.manager.jobs.job import Job


class JobDrive(Job):

    def __init__(self, **kwargs):
        super(JobDrive, self).__init__(**kwargs)
        self.controller_can_move = True
        self.state_returned = threading.Event()

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def run_threaded(self, user_throttle=None):
        # TODO : read for throttle change to trigger timer
        # TODO : return manager output for controller to 'lock / unlock' it
        self.logger.debug("run_threaded: throttle: %i", user_throttle)

        self.state_returned.set()
        return user_throttle if self.controller_can_move else 0.0, 'DRIVE'

    def run_job(self) -> None:
        # TODO : cancel on cancel flag set .. as soon as possible
        # TODO : set timer/timeout of the run length
        # TODO : output laptimer for reset at start, or start it's run condition anyway
        # TODO : wait until car starts moving (event from run_threader)
        self.logger.debug(f"JobDrive: start job_id:{self.get_id()}")

        self.controller_can_move = True
        self.state_returned.clear()

        #if "drive_time" in self.parameters:
        self.event_cancelled.wait(timeout=60)

        return
