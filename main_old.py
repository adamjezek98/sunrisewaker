import socket
import json
import neopixel
import machine
import utime

LED_COUNT = 150
WAKE_AT = 1515186530

f = open("wake_at.txt","r")
WAKE_AT = int(f.readline())
f.close()
print("will wake at", WAKE_AT)

def http_get(url, port=80):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    response = ""
    while True:
        data = s.recv(100)
        if data:
            response += str(data, 'utf8')
        else:
            break
    s.close()
    return response.split("\r\n\r\n")[1]


def get_timestamp():
    req = http_get("http://api.timezonedb.com/v2/get-time-zone?key=2BY1VUEDLEAY&format=json&by=zone&zone=Europe/Prague")
    return json.loads(req)["timestamp"]


np = neopixel.NeoPixel(machine.Pin(14), LED_COUNT)


def blink(freq, duration_ms=15*1000):
    delay = 1000 / freq
    start_time = utime.ticks_ms()
    while 1:
        np.fill((255, 255, 255))
        np.write()
        utime.sleep_ms(int(delay))
        np.fill((0, 0, 0))
        np.write()
        utime.sleep_ms(int(delay))
        if utime.ticks_ms() > start_time + duration_ms:
            break


while 1:
    try:
        tmstp = get_timestamp()
        print("now is", tmstp, "will wake at",WAKE_AT)
        if tmstp > WAKE_AT:
            blink(10000, 35*1000)
        utime.sleep_ms(10*1000)
    except KeyboardInterrupt:
        break
    except:
        pass