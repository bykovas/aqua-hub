import json
import os
import time
from datetime import datetime, timedelta, time as dt_time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ScheduleEntry:
    def __init__(self, time, coral_plus, blue_plus):
        self.time = time
        self.coral_plus = coral_plus
        self.blue_plus = blue_plus
        self.parsed_time = self.parse_time(time)

    def parse_time(self, time_str):
        return datetime.strptime(time_str, "%H:%M:%S").time()


class Schedule:
    _demo_mode_expire_time = None
    _current_schedule = []

    def __init__(self):
        self.load_schedule("ReefMoreBlue")
        self.setup_watcher()

    def setup_watcher(self):
        observer = Observer()
        handler = FileSystemEventHandler()
        handler.on_modified = self.on_changed
        observer.schedule(handler, path='.', patterns=['schedule.json'])
        observer.start()

    def on_changed(self, event):
        self.load_schedule("ReefMoreBlue")

    def load_schedule(self, schedule_name):
        with open('schedule.json', 'r') as f:
            schedules = json.load(f)
        self._current_schedule = [ScheduleEntry(**entry) for entry in schedules[schedule_name]]

    def calculate_current_values(self):
        now = datetime.now().time()
        current_blue_plus = None
        current_coral_plus = None

        for i in range(len(self._current_schedule) - 1):
            start = self._current_schedule[i].parsed_time
            end = self._current_schedule[i + 1].parsed_time

            if start <= now <= end:
                if self._current_schedule[i].blue_plus is not None or self._current_schedule[i + 1].blue_plus is not None:
                    current_blue_plus = int(self.interpolate(
                        self._current_schedule[i].blue_plus, self._current_schedule[i + 1].blue_plus, start, end, now))

                if self._current_schedule[i].coral_plus is not None or self._current_schedule[i + 1].coral_plus is not None:
                    current_coral_plus = int(self.interpolate(
                        self._current_schedule[i].coral_plus, self._current_schedule[i + 1].coral_plus, start, end, now))

        return [current_blue_plus or 0, current_coral_plus or 0]

    def interpolate(self, start_value, end_value, start_time, end_time, current_time):
        start_value = start_value or 0
        end_value = end_value or 0

        fraction = ((datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), start_time)).total_seconds() /
                    (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).total_seconds())
        return start_value + (end_value - start_value) * fraction

    def set_demo_mode(self, seconds=None):
        self._demo_mode_expire_time = datetime.now() + timedelta(seconds=seconds or 30)

    def is_demo_mode(self):
        return self._demo_mode_expire_time > datetime.now()
