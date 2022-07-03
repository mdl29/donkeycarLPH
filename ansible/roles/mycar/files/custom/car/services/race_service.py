import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, NoReturn, List

from custom.generic_worker.helpers.RegistableEvents import RegistableEvent
from custom.generic_worker.services.manager_api_service import ManagerApiService
from custom.generic_worker.models.schemas import Player, Car, RaceCreate, Race, LapTimerCreate, LapTimer


class RaceService:

    def __init__(self, api: ManagerApiService, player: Player, car: Car, max_duration: int):
        """
        :param api:
        :param player:
        :param car:
        :param max_duration: Max race duration in sec, purely indicative.
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self._api = api
        self.car = car
        self.player = player
        self.max_duration = max_duration

        self.race: Optional[Race] = None
        self.last_lap_end_date: Optional[datetime] = None
        self.is_reset = False
        self.is_ended = False

        self.laptimers: List[LapTimer] = []
        self.event_race_started = RegistableEvent() # Set every time a new lap is added

    def lazy_create_race(self, start: datetime) -> NoReturn:
        """
        As we need the start date to create a race, create if not already created.
        :param start:
        """

        if self.race is None:
            self.event_race_started.set()
            self.race = self._api.create_race(
                RaceCreate(
                    player_id=self.player.player_id,
                    stage=self.car.current_stage,
                    car_name=self.car.name,
                    start_datetime=start,
                    max_duration=self.max_duration
                )
            )
            self.car.current_race_id = self.race.race_id
            self._api.update_car(car=self.car)
            self.logger.debug('Created race (race_id: %i), for %s started at %s',
                              self.race.race_id, self.player.player_pseudo, start)

    def handle_laptimer_outputs(self,
                                laptimer_current_start_lap_datetime: Optional[datetime] = None,
                                laptimer_current_lap_duration: Optional[int] = None,
                                laptimer_last_lap_start_datetime: Optional[datetime] = None,
                                laptimer_last_lap_duration: Optional[int] = None,
                                laptimer_last_lap_end_date_time: Optional[datetime] = None,
                                laptimer_laps_total: Optional[int] = None) -> bool:
        """
        :param laptimer_current_start_lap_datetime:
        :param laptimer_current_lap_duration:
        :param laptimer_last_lap_start_datetime:
        :param laptimer_last_lap_duration:
        :param laptimer_last_lap_end_date_time:
        :param laptimer_laps_total:
        :return: True if we want to reset race.
        """
        if self.is_ended: # No race, can reset laptimers
            return True

        if not self.is_reset:  # First reset it
            self.is_reset = True
            return True

        if laptimer_current_start_lap_datetime is None:
            return False

        self.lazy_create_race(laptimer_current_start_lap_datetime)

        # New lap ended
        if laptimer_last_lap_end_date_time is not None and self.last_lap_end_date !=  laptimer_last_lap_end_date_time:

            if laptimer_last_lap_start_datetime is None or laptimer_last_lap_end_date_time is None:
                self.logger.error('One of the following is None and shouldn\'t be, laptimer_last_lap_start_datetime: %s, laptimer_last_lap_end_date_time: %s',
                                  laptimer_last_lap_start_datetime, laptimer_last_lap_end_date_time)
                return False

            if laptimer_last_lap_duration is None:  # Shouldn't happen but we have strangely seen it already
                self.logger.warning('laptimer_last_lap_duration was None, had to recalculate it, it should be done by the part')
                laptimer_last_lap_duration = (datetime.now(timezone.utc) - self.timer.current_start_lap_date) / timedelta(
                    milliseconds=1)
                self.logger.warning('laptimer_last_lap_duration is now : %i ms', laptimer_last_lap_duration)

            self.last_lap_end_date = laptimer_last_lap_end_date_time
            laptimer =  self._api.create_laptimer(LapTimerCreate(
                race_id=self.race.race_id,
                start_datetime=laptimer_last_lap_start_datetime,
                duration=laptimer_last_lap_duration,
                end_datetime=laptimer_last_lap_end_date_time
            ))
            self.laptimers.append(laptimer)
            self.logger.debug('New lap ended, created (lap_id: %i), for %s, duration: %i',
                              laptimer.laptimer_id, self.player.player_pseudo, laptimer.duration)

        return False

    def end(self):
        """
        End the race, reset lap timer.
        """
        self.is_ended = True
