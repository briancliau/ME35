import network
import time
import uasyncio as asyncio

SSID = "tufts_eecs" #use tufts_eecs
PASSWORD = "foundedin1883" #foundedin1883
PORT = 80

# Latest battery readings (-1 = none received yet)
iphone_battery = -1
ipad_battery = -1

# Latest focus-event results: None, "good" or "bad"
event1_status = None
event2_status = None

# Hooks: main.py assigns these so the server stays a thin network layer
on_battery = None    # fn(device, level)
on_charger = None    # fn(device, state, level)
on_event = None      # fn(event, result)
on_learning = None   # fn(True | False | None) -> current learning state (None = just read it)
get_status = None    # fn() -> str


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting", end="")
        wlan.connect(SSID, PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        print()
    if not wlan.isconnected():
        raise RuntimeError("Wi-Fi connection failed")
    print("ESP32 IP:", wlan.ifconfig()[0])
    return wlan


def parse_request(request):
    # Request line looks like: GET /trigger?event=1&result=bad HTTP/1.1
    params = {}
    try:
        line = request.split("\r\n")[0]
        full_path = line.split(" ")[1]
        if "?" in full_path:
            path, query = full_path.split("?", 1)
            for pair in query.split("&"):
                key, _, value = pair.partition("=")
                params[key] = value
        else:
            path = full_path
        return path, params
    except Exception as e:
        print("Parse error:", e)
        return None, {}


async def respond(writer, status, body):
    writer.write("HTTP/1.1 {}\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n{}".format(status, body).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def handle_battery(writer, params):
    global iphone_battery, ipad_battery

    if "level" not in params or "device" not in params:
        await respond(writer, "400 Bad Request", "Use /battery?device=iphone|ipad&level=NN")
        return

    try:
        level = int(float(params["level"]))
    except ValueError:
        await respond(writer, "400 Bad Request", "Bad level")
        return

    device = params["device"].lower()
    if device == "iphone":
        iphone_battery = level
        print("iPhone battery: {}%".format(iphone_battery))
    elif device == "ipad":
        ipad_battery = level
        print("iPad battery: {}%".format(ipad_battery))
    else:
        await respond(writer, "403 Forbidden", "Unknown device")
        return

    if on_battery:
        on_battery(device, level)
    await respond(writer, "200 OK", "OK")


async def handle_trigger(writer, params):
    global event1_status, event2_status

    event = params.get("event", "")
    result = params.get("result", "").lower()

    if event not in ("1", "2") or result not in ("good", "bad"):
        await respond(writer, "400 Bad Request", "Use /trigger?event=1|2&result=good|bad")
        return

    if event == "1":
        event1_status = result
    else:
        event2_status = result

    print("Event {}: {}".format(event, result))
    if on_event:
        on_event(event, result)
    await respond(writer, "200 OK", "OK")


async def handle_charger(writer, params):
    """Optional: tells the robot when a device is plugged in / unplugged."""
    device = params.get("device", "").lower()
    state = params.get("state", "")

    if device not in ("iphone", "ipad"):
        await respond(writer, "403 Forbidden", "Unknown device")
        return
    if state not in ("connected", "disconnected"):
        await respond(writer, "400 Bad Request", "Use /charger?device=iphone|ipad&state=connected|disconnected")
        return

    level = -1
    if state == "connected":
        try:
            level = int(float(params.get("level", "")))
        except ValueError:
            await respond(writer, "400 Bad Request", "Need level when connected")
            return

    print("Charger {}: {}".format(device, state))
    if on_charger:
        on_charger(device, state, level)
    await respond(writer, "200 OK", "OK")


async def handle_learning(writer, params):
    """/learning?state=on|off switches KNN learning; /learning alone reports it."""
    state = params.get("state", "").lower()
    value = None
    if on_learning:
        if state in ("on", "off"):
            value = on_learning(state == "on")
        else:
            value = on_learning(None)
    await respond(writer, "200 OK", "learning " + ("on" if value else "off"))


async def handle(reader, writer):
    try:
        request = (await reader.read(1024)).decode()
    except Exception as e:
        print("Read error:", e)
        writer.close()
        await writer.wait_closed()
        return

    path, params = parse_request(request)

    if path == "/battery":
        await handle_battery(writer, params)
    elif path == "/trigger":
        await handle_trigger(writer, params)
    elif path == "/charger":
        await handle_charger(writer, params)
    elif path == "/learning":
        await handle_learning(writer, params)
    elif path == "/status":
        await respond(writer, "200 OK", get_status() if get_status else "no status")
    else:
        await respond(writer, "404 Not Found", "Unknown path")


async def start():
    await asyncio.start_server(handle, "0.0.0.0", PORT)
    print("Server running")

