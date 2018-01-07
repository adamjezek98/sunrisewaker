import http
import http.server
import alarmclock as ac
from urllib import parse
import templates
import config
import datetime
import sqlite3

files = (".ico", ".png", ".css", ".js")


class WebHandler(http.server.SimpleHTTPRequestHandler):
    # def log_message(self, format, *args):
    #    return

    webProcessor = None

    def do_GET(self):
        path = self.path
        webProcessor = WebProcessor()

        if self.checkEnds(path, files):
            try:
                f = open("files/" + path[1:], "rb")
                self.send_response(200)
                # self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            except IOError:
                self.send_error(404, 'File Not Found: %s' % path)

        else:
            try:
                result = webProcessor.process(path)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(str(result), "utf-8"))
            except Exception as ex:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                result = "<h1>HTTP 500</h1><br/>"
                self.wfile.write(bytes(result + str(ex), "utf-8"))
                raise ex

    def checkEnds(self, line, ends):
        return any(line.endswith(end) for end in ends)


class WebProcessor():
    def __init__(self):
        self.alarmClock = ac.AlarmClock()
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def process(self, path):
        if path == "/getstate":
            result = self.process_alarmclock(path)
        else:
            result = self.proccess_user(path)
        return result

    def proccess_user(self, path):
        params = parse.parse_qs(path.split("?")[-1])
        print(params)
        path = path.split("?")[0]
        title = "Alarms"
        body = ""
        if path == "/":  # list alarm clocks
            body += "Server time {time}".format(time=datetime.datetime.now())
            alarms = self.alarmClock.get_alarms_sorted_by_nearest_day(False)
            tbody = ""
            for alarm in alarms:
                alarm = dict(alarm)
                alarm = self.fill_alarm_for_table(alarm)
                table_line = templates.TBODY.format(**alarm)
                tbody += table_line
            body += templates.TABLE.format(tbody=tbody)
        elif "/edit/" in path:
            id = path.split("/edit/")[-1].replace("/", "")
            body += self.edit_page(id)
        elif "/set/" in path:
            return self.set_alarm(params)

        return templates.HTML_BASE.format(title=title, body=body)

    def fill_alarm_for_table(self, alarm):
        if alarm["repeat"] == -1:
            alarm["remaining_repeats"] = "Infinite"
        else:
            alarm["remaining_repeats"] = alarm["repeat"]

        days = self.days
        active_days = ""
        for i in alarm["day"].split(","):
            active_days += days[int(i)] + ", "

        for i in range(len(days)):
            if str(i) in alarm["day"]:
                alarm[days[i].lower()] = "checked"
            else:
                alarm[days[i].lower()] = ""

        if active_days.endswith(", "):
            active_days = active_days[:-2]

        alarm["active_days"] = active_days
        return alarm

    def edit_page(self, id):
        alarm = self.alarmClock.get_alarm_by_id(id)
        body = templates.ALARM_EDIT.format(**self.fill_alarm_for_table(alarm))
        body += templates.FORM_JS
        return body

    def set_alarm(self, params):
        print(params)
        for i in params.keys():
            params[i] = params[i][0]
        db = sqlite3.connect(config.db_file)
        c = db.cursor()
        days = ""
        for i, day in enumerate(self.days):
            if day.lower() in params.keys():
                days += str(i)+","
        if days.endswith(","):
            days = days[:-1]
        c.execute("""UPDATE wakeups SET name=?, hour=?, minute=?, repeat=?, duration=?, day=?, 
                  start_at=NULL, start_at_string=NULL WHERE id=?""",
                  [params["name"], params["hour"], params["minute"], params["repeat"],
                   int(params["duration"]), days, int(params["id"])])
        db.commit()
        return "OK"

        return str(params)

    def process_alarmclock(self, path):

        alarm = self.alarmClock.calc_nearest_alarm()
        col = str(alarm["light_color"]).replace(" ", "").replace("]", "").replace("[", "")
        return col


server = http.server.HTTPServer(("0.0.0.0", config.server_port), WebHandler)
while 1:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        break
    except:
        pass
