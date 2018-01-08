# how long after the alarm time is achieved should the strip blink (in minutes)
blink_after = 15

# the color of strip that should be achieved at fully brightness
sunrise_rgb = (255, int(255 / 2), 0)

project_home = "/home/pi/sunrisewaker"
import os
os.chdir(project_home)

# database file
db_file = project_home + "alarmclock.sqlite3"

# port for web config
server_port = 5000
# serial port with Arduino
arduino_port = "/dev/ttyACM0"