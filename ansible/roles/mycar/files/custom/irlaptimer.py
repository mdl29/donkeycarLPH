from typing import Optional

from evdev import InputDevice, ecodes
from time import time
import threading
from datetime import datetime, timedelta, timezone
import sys
import logging

class IrLapTimer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self.device = InputDevice('/dev/input/event0')
        self.current_start_lap_date: Optional[datetime] = None
        self.last_lap_start_date: Optional[datetime] = None
        self.last_lap_duration: Optional[int] = None
        self.last_lap_end_date: Optional[datetime] = None
        self.laps_total = 0
        self.daemon = True
        return

    def run(self):
        last_time_was = 0
        laps_delay_validation = 3 # seconds
        for event in self.device.read_loop():

            if event.type == ecodes.EV_MSC and event.value == 131380: # receive a scancode of 0x20134
                event_time_seconds = event.timestamp()

                # avoid rapid firing
                if last_time_was == 0 or event_time_seconds > (last_time_was + laps_delay_validation):
                    last_time_was = event_time_seconds
                    event_datetime = datetime.fromtimestamp(event_time_seconds, tz=timezone.utc)

                    # This is the first time IR are seen, means we only start a lap
                    if self.laps_total == 0:
                        self.current_start_lap_date = event_datetime
                        self.logger.debug('[lap nb %i] First lap starting now : %s', self.laps_total,
                                          self.current_start_lap_date)
                        self.laps_total += 1
                        continue

                    # We know we are at the end of a lap and begining of a new one :)
                    # save the last time when the event was received
                    self.last_lap_end_date = event_datetime
                    self.last_lap_start_date = self.current_start_lap_date
                    self.current_start_lap_date = event_datetime

                    self.logger.debug('[lap nb %i] last_lap_end_date: %s', self.laps_total, self.last_lap_end_date)
                    self.logger.debug('[lap nb %i] current_start_lap_date: %s', self.laps_total, self.current_start_lap_date)

                    self.last_lap_duration = (self.last_lap_end_date - self.last_lap_start_date) / timedelta(milliseconds = 1)

                    self.logger.debug('[lap nb %i] last_start_lap_date: %s', self.laps_total, self.last_lap_start_date)
                    self.logger.info('[lap nb %i] last_lap_duration: %i', self.laps_total, self.last_lap_duration)

                    self.laps_total += 1

class IrLapTimerPart:
    def __init__(self):
        self.timer = IrLapTimer()
        self.timer.start()
    def update(self):
        return
    def run_threaded(self, reset_all = False):
        if reset_all:
            self.timer.current_start_lap_date= None
            self.timer.last_lap_start_date= None
            self.timer.last_lap_duration = None
            self.timer.last_lap_end_date = None
            self.timer.laps_total = 0
        current_lap_duration = None
        if self.timer.current_start_lap_date:
            current_lap_duration = (datetime.now(timezone.utc) - self.timer.current_start_lap_date) / timedelta(milliseconds = 1)
        return self.timer.current_start_lap_date, current_lap_duration, self.timer.last_lap_start_date, self.timer.last_lap_duration, self.timer.last_lap_end_date, self.timer.laps_total
    def run(self, reset_all = False):
        return self.run_threaded(reset_all)