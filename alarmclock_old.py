import config
import sqlite3
import datetime


class AlarmClock():
    def __init__(self):
        self.db = sqlite3.connect(config.db_file)
        self.db.row_factory = sqlite3.Row
        self.c = self.db.cursor()

    def get_alarm_by_id(self, id):
        self.c.execute("""SELECT * FROM wakeups WHERE id == ?""", [str(id)])
        alarm = dict(self.c.fetchone())
        return alarm

    def get_alarms_sorted_by_nearest_day(self, active_only=True):
        alarms = []
        """9 selects for 7 days in a week
        during first run, today's alarms with hour = now and minute > now are selected
        during secon run, today's alarms with hour > now+1 are selected
        then each day is added to the list
        and at the end ('9th' day), wo again choose todays alarm with hour < now
        in the result, we have ALL active alarms from db, sorted from nearest to lastest"""
        for add_day in range(9):
            day = 0
            hour = 0
            minute = 0
            if add_day == 0:
                add_day = 1
                hour = datetime.datetime.now().hour
                minute = datetime.datetime.now().minute
            elif add_day == 1:
                hour = datetime.datetime.now().hour+1
                minute = 0
            add_day -= 1
            day = (datetime.datetime.now().weekday() + add_day) % 7
            #print(add_day, day, hour, minute)
            self.c.execute("""SELECT * FROM wakeups
                             WHERE day LIKE ? AND (repeat != 0 OR ?) AND hour >= ? AND minute >= ?
                             ORDER BY hour ASC""",
                           ["%" + str(day) + "%", str(int(not active_only)), str(hour), str(minute)])
            for alarm in self.c.fetchall():
                if alarm not in alarms:
                    alarms.append(alarm)

        return alarms

    def calc_nearest_alarm(self):
        alarms = self.get_alarms_sorted_by_nearest_day()
        # first, check if any alarm didn't recently ended
        alarm = alarms[-1]
        #print(self.calc_alarm_time_delta(alarm), (7 * 24 * 60) - (config.blink_after ) )
        if self.calc_alarm_time_delta(alarm) > (7 * 24 * 60) - (config.blink_after ):
            ret = {"alarm": alarm,
                   "should_start": True,
                   "activate_in": 0,
                   "percentage": 100,
                   "light_color": "blink"}
            return ret

        alarm = alarms[0]
        activate_in = self.calc_alarm_time_delta(alarm)

        perc = 0
        should_start = False
        light_color = list(config.sunrise_rgb)
        if activate_in < alarm["duration"]:
            perc = ((alarm["duration"] - activate_in) * 100) / alarm["duration"]
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
