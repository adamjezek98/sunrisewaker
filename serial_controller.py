import config
import alarmclock
import serial
import time
alarmClock = alarmclock.AlarmClock()
serial_port = serial.Serial(config.arduino_port, 115200)

while 1:
    alarm = alarmClock.calc_nearest_alarm()
    if alarm["light_color"] == "blink":
        serial_port.write(bytes("sb:","utf-8"))
    else:
        col = str(alarm["light_color"]).replace(" ", "").replace("]", "").replace("[", "")
        serial_port.write(bytes("sl:"+col.replace(",",":"), "utf-8"))

    time.sleep(5)