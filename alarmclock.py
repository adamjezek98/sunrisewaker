import config
import sqlite3
import datetime
import time


class AlarmClock():
    def __init__(self):
        self.db = sqlite3.connect(config.db_file)
        self.db.row_factory = sqlite3.Row
        self.c = self.db.cursor()

    def get_alarm_by_id(self, id):
        self.c.execute("""SELECT * FROM wakeups WHERE id == ?""", [str(id)])
        alarm = dict(self.c.fetchone())
        return alarm

    def fill_alarms_timestamps(self):
        # get all alarms that should be launched in future
        self.c.execute("""SELECT * FROM wakeups WHERE repeat != 0""")
        now = int(time.time())
        for alarm in self.c.fetchall():
            # alarm happend before (now + blink_after minutes), or has no happend time yet
            if alarm["start_at"] is None or alarm["start_at"] < now - (config.blink_after * 60):
                print(dict(alarm), self.calc_alarm_time_delta(alarm))
                # first calculate how many repeats has alarm left
                repeat = -1 if alarm["repeat"] == -1 else alarm["repeat"] - 1
                if repeat == 0 and alarm["start_at"] is not None:  # if there is none left, but the alarm didn't happend
                    alarm_timestamp = None
                    will_run_at = None
                else:
                    # get days remaining to launch the alarm
                    remaining_days = ((self.nearest_alarm_day(alarm) - datetime.datetime.now().weekday()) + 7) % 7
                    if remaining_days == 0:
                        if self.calc_alarm_time_delta(alarm) > 60 * 24:
                            # if days difference is 0, it means today, but if timedelta si more than one day,
                            # it means today in next week
                            remaining_days = 7
                    alarm_date = datetime.datetime.now().replace(hour=alarm["hour"], minute=alarm["minute"], second=0,
                                                                 microsecond=0)
                    alarm_date += datetime.timedelta(days=remaining_days)
                    # get next alarm launch
                    alarm_timestamp = time.mktime(alarm_date.timetuple())
                    # just to easily make sure timestamp was calculated correnctly
                    will_run_at = datetime.datetime.fromtimestamp(alarm_timestamp)
                    will_run_at = will_run_at.strftime("%a, %H:%M, %b %d. %y")
                self.c.execute("""UPDATE wakeups SET repeat = ?, start_at = ?, start_at_string = ? WHERE id = ?;""",
                               [repeat, alarm_timestamp, will_run_at, alarm["id"]])
        self.db.commit()

    def get_alarms_sorted_by_nearest_day(self, active_only=True):
        alarms = []
        active_time = int(time.time()) - config.blink_after * 60
        self.c.execute("""SELECT * FROM wakeups WHERE start_at >= ?  ORDER BY start_at ASC""",
                       [active_time])
        for alarm in self.c.fetchall():
            alarms.append(dict(alarm))
        if not active_only:
            self.c.execute("""SELECT * FROM wakeups WHERE start_at < ?  ORDER BY start_at ASC""",
                           [active_time])
            for alarm in self.c.fetchall():
                alarms.append(dict(alarm))

        return alarms

    def calc_nearest_alarm(self):
        alarm = self.get_alarms_sorted_by_nearest_day()[0]
        now = int(time.time())
        # seconds to start the alarm
        activate_in = alarm["start_at"] - now

        # if alarm is already activated, get_alarms_sorted_by_nearest_day makes sure it is only if it ended
        # befory config.blink_after minutes
        if activate_in < 0:
            ret = {"alarm": alarm,
                   "should_start": True,
                   "activate_in": 0,
                   "percentage": 100,
                   "light_color": "blink"}
            return ret

        perc = 0
        should_start = False
        light_color = list(config.sunrise_rgb)
        if activate_in < alarm["duration"] * 60:
            perc = 100 - ((100 * activate_in) / (alarm["duration"] * 60))
            should_start = True
        for i in range(len(light_color)):
            light_color[i] = int(perc * (light_color[i] / 100))

        ret = {"alarm": alarm,
               "should_start": should_start,
               "activate_in": activate_in,
               "percentage": perc,
               "light_color": light_color}
        return ret

    def calc_alarm_time_delta(self, alarm):
        now = datetime.datetime.now().time().replace(second=0, microsecond=0)
        now = datetime.datetime.combine(datetime.datetime.today(), now)
        al = datetime.time(hour=alarm["hour"], minute=alarm["minute"])
        al = datetime.datetime.combine(datetime.datetime.today(), al)
        delta = (al - now).seconds / 60
        remaining_days = ((self.nearest_alarm_day(alarm) - now.weekday()) + 7) % 7

        if remaining_days > 0:
            if (al - now).days < 0:
                delta = ((remaining_days - 1) * 24 * 60) + delta
        elif remaining_days == 0:
            if (al - now).days < 0:
                delta = (6 * 24 * 60) + delta
        return int(delta)

    def nearest_alarm_day(self, alarm):
        today = datetime.datetime.now().weekday()
        now = datetime.datetime.now()
        for add_day in range(7):
            if add_day == 0:
                if alarm["hour"] * 60 + alarm["minute"] < now.hour * 60 + now.minute:
                    continue
            if str((today + add_day) % 7) in alarm["day"]:
                return (today + add_day) % 7
        return today


if __name__ == "__main__":

    alarmClock = AlarmClock()
    while 1:
        alarmClock.fill_alarms_timestamps()
        time.sleep(5)
