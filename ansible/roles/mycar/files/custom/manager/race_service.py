import logging
from datetime import datetime
from typing import Optional, NoReturn, List

from custom.manager.car_manager_api_service import CarManagerApiService
from custom.manager.schemas import Player, Car, RaceCreate, Race, LapTimerCreate, LapTimer


class RaceService:

    def __init__(self, api: CarManagerApiService, player: Player, car: Car):
        """
        :param api:
        :param player:
        :param car:
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self._api = api
        self.car = car
        self.player = player

        self.race: Optional[Race] = None
        self.last_lap_end_date: Optional[datetime] = None
        self.is_reset = False
        self.is_ended = False

        self.laptimers: List[LapTimer] = []

    def lazy_create_race(self, start: datetime) -> NoReturn:
        """
        As we need the start date to create a race, create if not already created.
        :param start:
        """

        if self.race is None:
            self.race = self._api.create_race(
                RaceCreate(
                    player_id=self.player.player_id,
                    stage=self.car.current_stage,
                    car_name=self.car.name,
                    start_datetime=start
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
