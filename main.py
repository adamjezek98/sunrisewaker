import socket
import json
import neopixel
import machine
import utime

LED_COUNT = 120

URL = "http://192.168.5.140/getstate"
PORT = 5000

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


def get_color():
    color = http_get(URL, PORT)
    return color


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
    utime.sleep_ms(10*1000)
    try:
        col = get_color()
        print("color is", col)
        if "blink" in col:
            blink(1000)
        elif "," in col:
            color = []
            for c in col.split(","):
                color.append(int(c))
            np.fill(color)
            np.write()
    except KeyboardInterrupt:
        break
    except Exception as ex:
        print(str(ex))
        pass