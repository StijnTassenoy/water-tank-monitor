import utime
import ntptime
import uerrno
import uselect
import ujson
import network
import socket
import credentials
from machine import Pin

tank_height_cm = 200.00


def set_correct_time():
    print("[!] Trying to set correct time...")
    retry_count = 5
    while retry_count > 0:
        try:
            print(utime.localtime())
            ntptime.settime()
            print(utime.localtime())
            print("[!] Time set!")
            break
        except Exception as e:
            print(f"[!] {e}")
            print("[!] Failed to set time. Retrying...")
            print("[!] Remaining retries: ", retry_count)
            retry_count -= 1
            utime.sleep(0.1)
            if retry_count == 0:
                print("[!] Out of retries. Continuing with incorrect time...")
                break

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
    """ Calculate the height of the tank in percent and actual fill. """
    true_fill = tank_height - ultrasonic_dst
    percentage_fill = int((true_fill / tank_height) * 100)
    return true_fill, percentage_fill


def distance_handler():
    """ API endpoint to get the current ultrasonic measurement. """

    distance = measure_ultrasonic()
    true_fill, percentage_fill = calculate_tank_fill(tank_height_cm, distance)
    response_body = {
        "timestamp": str(int(utime.time())),
        "distance": str(distance),
        "fill": true_fill,
        "percentage": percentage_fill
    }
    print(f"[i] Measured: {str(response_body)}")

    with open("history.json", "r") as f:
        lines = f.readlines()
        if not lines or not lines[0].startswith("{"):
            print("[+] Creating history json...")
            history = {"history": []}
        else:
            print("[i] Loading history json...")
            history = ujson.loads("".join(lines))
    if len(history["history"]) >= 10:
        history["history"].pop(0)
    history["history"].append(response_body)
    with open("history.json", "w") as f:
        ujson.dump(history, f)
    print(f"[+] Added distance ({distance}) to history.")

    return ujson.dumps(response_body)


def history_handler():
    """ API endpoint to get the ultrasonic measurement history. """
    with open("history.json", "r") as f:
        lines = f.readlines()
        print(f"readlines: {lines}")
        if not lines or not lines[0].startswith("{"):
            history = {"history": []}
        else:
            history = ujson.loads("".join(lines))
        print(f"history: {history}")
    return ujson.dumps(history)


def main():
    ssid = credentials.ssid
    password = credentials.password
    ip_address = "192.168.0.18"
    server_port = 80

    print("Watertank Monitor...")

    connect_to_wlan(ip_address, ssid, password)
    set_correct_time()

    server = socket.socket()
    server.bind((ip_address, server_port))
    server.listen(1)
    print("Listening on", ip_address)

    html = "Status: OK"

    headers = {
        "Content-Type": "application/json",
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
                        response_body = distance_handler()
                    elif path == "/history":
                        response_body = history_handler()
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
