import utime
import uerrno
import uselect
import ujson
import network
import socket
import credentials
from machine import Pin


def connect_to_wlan(static_ip: str, ssid: str, password=None):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    wlan.ifconfig((static_ip, "255.255.255.0", "192.168.0.1", "1.1.1.1"))

    # Wait for connection
    while not wlan.isconnected():
        utime.sleep(1)


def measure_ultrasonic() -> float:
    """ Measure the ultrasonic sensor's distance from an object. """
    trigger = Pin(3, Pin.OUT)
    echo = Pin(2, Pin.IN)

    signal_on = 0
    signal_off = 0

    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()
    while echo.value() == 0:
        signal_off = utime.ticks_us()
    while echo.value() == 1:
        signal_on = utime.ticks_us()
    time_passed = signal_on - signal_off

    distance_cm = (time_passed * 0.0343) / 2
    distance_cm = round(distance_cm, 2)
    return distance_cm


def calculate_tank_fill(tank_height: float, ultrasonic_dst: float) -> tuple[float, int]:
    true_fill = tank_height - ultrasonic_dst
    percentage_fill = int((true_fill / tank_height) * 100)
    return true_fill, percentage_fill


def main():
    ssid = credentials.ssid
    password = credentials.password
    ip_address = "192.168.0.18"
    server_port = 80
    tank_height_cm = 200.00

    print("Watertank Monitor...")

    connect_to_wlan(ip_address, ssid, password)

    server = socket.socket()
    server.bind((ip_address, server_port))
    server.listen(1)
    print("Listening on", ip_address)

    with open("index.html", "r") as f:
        html = f.read()

    headers = {
        "Content-Type": "text/html",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    while True:
        try:
            r, w, e = uselect.select([server], [], [], 0)
            if r:
                client_sock, client_addr = server.accept()
                request = client_sock.recv(1024)
                if request:
                    request_str = request.decode("utf-8")
                    request_lines = request_str.split("\r\n")
                    method, path, protocol = request_lines[0].split(" ")
                    if path == "/distance":
                        distance = measure_ultrasonic()
                        true_fill, percentage_fill = calculate_tank_fill(tank_height_cm, distance)
                        response_body = {
                            "distance": str(distance),
                            "fill": true_fill,
                            "percentage": percentage_fill
                        }
                        response_body = ujson.dumps(response_body)
                        print(response_body)
                    else:
                        response_body = html
                    response = "HTTP/1.1 200 OK\r\n"
                    for header, value in headers.items():
                        response += "{}: {}\r\n".format(header, value)
                    response += "\r\n{}".format(response_body)
                    client_sock.send(response.encode("utf-8"))
                client_sock.close()
        except OSError as e:
            if e.args[0] == uerrno.EAGAIN:
                utime.sleep(0.1)
            else:
                raise e


if __name__ == "__main__":
    main()
