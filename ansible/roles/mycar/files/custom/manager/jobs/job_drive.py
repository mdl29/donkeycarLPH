import logging
import threading
from datetime import datetime
from enum import Enum
from typing import Tuple, Optional

from custom.helpers.conditional_events import ConditionalEvents, CondEventsOperator
from custom.helpers.RegistableEvents import RegistableEvent
from custom.manager.jobs.job import Job
from custom.manager.race_service import RaceService

DEFAULT_DRIVE_TIME_SEC = 5*60 # Default drive time is 4min

class JobDriveStage(int, Enum):
    # Stages orders USER_NOT_CONFIRMED > USER_DRIVING

    # At this stage, user isn't confirming meaning the job was started but we should pause it so that
    # the admin confirm manually to "resume" the job and asses it's the right user
    USER_NOT_CONFIRMED = 0

    # At this stage we know that the user as moved and the countdown is started
    # This stage comes after USER_NOT_CONFIRMED
    USER_CONFIRMED = 1

    # user start moving and drive session fully started
    USER_DRIVING = 2

    # Driving session is finished
    DRIVE_FINISHED = 3


class JobDrive(Job):

    def __init__(self, **kwargs):
        super(JobDrive, self).__init__(**kwargs)
        self.controller_can_move = False  # Default moving value, not enabled, will be enabled at start
        self.state_returned = RegistableEvent()  # used to report if run_threaded return the state
        self.user_start_moving = RegistableEvent()  # Set when the user/throttle changes

        self.drive_stage: JobDriveStage = JobDriveStage.USER_NOT_CONFIRMED

        self.drive_time = self.parameters["drive_time"] if "drive_time" in self.parameters else DEFAULT_DRIVE_TIME_SEC

        self.race_service = RaceService(self.api, self.job_data.player, car=self.car, max_duration=self.drive_time)

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def run_threaded(self,
                     user_throttle=None,
                     laptimer_current_start_lap_datetime: Optional[datetime] = None,
                     laptimer_current_lap_duration: Optional[int] = None,
                     laptimer_last_lap_start_datetime: Optional[datetime] = None,
                     laptimer_last_lap_duration: Optional[int] = None,
                     laptimer_last_lap_end_date_time: Optional[datetime] = None,
                     laptimer_laps_total: Optional[int] = None
                     ) -> Tuple[float, str, bool]:
        """
        Part run_threaded call.
        :param user_throttle: The user throttle, 0 when not moving.
        :return: [
            user_throttle,
            job_name,
            laptimer_reset_all,
            recording
            ]
        """
        laptimer_reset_all = True

        if self.drive_stage == JobDriveStage.USER_NOT_CONFIRMED: # user not confirmed yet
            return 0.0, 'DRIVE', laptimer_reset_all, False

        if user_throttle > 0.0:
            if not self.user_start_moving.isSet(): # Logging only first time
                self.logger.debug("[job_id: %i] user starts moving, user_throttle: %f", self.get_id(), user_throttle)
            self.user_start_moving.set()

        self.state_returned.set()

        if self.drive_stage == JobDriveStage.USER_DRIVING:
            laptimer_reset_all = self.race_service.handle_laptimer_outputs(
                laptimer_current_start_lap_datetime,
                laptimer_current_lap_duration,
                laptimer_last_lap_start_datetime,
                laptimer_last_lap_duration,
                laptimer_last_lap_end_date_time,
                laptimer_laps_total
            )

        return user_throttle if self.controller_can_move else 0.0, 'DRIVE', laptimer_reset_all, False

    def set_move(self, user_can_move: bool) -> threading.Event:
        """
        Set if the user can move or not.
        :param user_can_move: True enable the user to move, False will block throttle.
        :returns: The event if the caller wants to wait until state is set
        """
        self.controller_can_move = user_can_move
        self.state_returned.clear()
        return self.state_returned

    def run_job(self, resumed: bool = False) -> None:

        # Update stage based on resuming and current stage
        if resumed and self.drive_stage == JobDriveStage.USER_NOT_CONFIRMED:
            # Job was resumed, meaning now user is confirmed
            self.drive_stage = JobDriveStage.USER_CONFIRMED

        # Starts by pausing job, so that admin confirm the user
        if self.drive_stage == JobDriveStage.USER_NOT_CONFIRMED:
            self.logger.debug("job_id: %i] Pausing drive, ask for human to confirm the user as changed", self.get_id())
            self.pause()  # Pausing ourself

            with ConditionalEvents([self.event_cancelled, self.event_paused], CondEventsOperator.OR) as cancelled_or_paused:
                cancelled_or_paused.wait()
            return

        # Here we know user is confirmed
        if self.drive_stage == JobDriveStage.USER_CONFIRMED:
            self.logger.debug("[job_id: %i] start, waiting for user to move", self.get_id())
            self.set_move(True)

            with ConditionalEvents([self.event_cancelled, self.user_start_moving, self.event_paused], operator=CondEventsOperator.OR) as start_pause_or_cancelled:
                start_pause_or_cancelled.wait()

            if self.event_cancelled.isSet():
                self.drive_stage = JobDriveStage.DRIVE_FINISHED
                return

            if self.event_paused.isSet():
                return

            if self.user_start_moving.isSet():
                self.drive_stage = JobDriveStage.USER_DRIVING
                self.logger.debug("[job_id: %i] user start moving", self.get_id())

                with ConditionalEvents([self.event_cancelled, self.race_service.event_race_started], operator=CondEventsOperator.OR) as canceled_or_new_lap:
                    self.logger.debug('[job_id: %i] Waiting for race started or cancelled, before starting drive countdown',
                                      self.get_id())
                    canceled_or_new_lap.wait()

                self.logger.debug('[job_id: %i] User cross the start line (or cancelled job), race started, starting the time counter for drive: %i sec',
                                  self.get_id(),
                                  self.drive_time)
                self.event_cancelled.wait(timeout=self.drive_time)
                if self.event_cancelled.isSet(): # Cancelled before have finished is run :(
                    self.logger.warning('[job_id: %i] Drive canceled before having time to finish it', self.get_id())
                    self.drive_stage = JobDriveStage.DRIVE_FINISHED
                    return

                # Drive timeout, setting can_move to false and ensure it's set
                self.logger.debug('[job_id: %i]  Driving session finished', self.get_id())
                self.set_move(False) # Not waiting as False is the default state, even this line could be removed
                self.drive_stage = JobDriveStage.DRIVE_FINISHED
