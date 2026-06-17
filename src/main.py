import network
import socket
import espnow
from machine import Pin

# =====================
# ESP-NOW
# =====================

sta = network.WLAN(network.STA_IF)
sta.active(True)

e = espnow.ESPNow()
e.active(True)

# Replace with TRAIN ESP MAC
TRAIN_MAC = b'\x38\x18\x2b\x8b\xd7\x9c'

e.add_peer(TRAIN_MAC)


def send_train_command(command):
    e.send(TRAIN_MAC, command)


# =========================
# LED SETUP (T1 → T6)
# =========================

semaphores = {
    "T1": {
        "red": Pin(15, Pin.OUT),
        "yellow": Pin(2, Pin.OUT),
        "green": Pin(4, Pin.OUT),
    },
    "T2": {
        "red": Pin(16, Pin.OUT),
        "yellow": Pin(17, Pin.OUT),
        "green": Pin(5, Pin.OUT),
    },
    "T3": {
        "red": Pin(18, Pin.OUT),
        "yellow": Pin(19, Pin.OUT),
        "green": Pin(21, Pin.OUT),
    },
    "T4": {
        "red": Pin(22, Pin.OUT),
        "yellow": Pin(23, Pin.OUT),
        "green": Pin(25, Pin.OUT),
    },
    "T5": {
        "red": Pin(26, Pin.OUT),
        "yellow": Pin(27, Pin.OUT),
        "green": Pin(14, Pin.OUT),
    },
    "T6": {
        "red": Pin(32, Pin.OUT),
        "yellow": Pin(33, Pin.OUT),
        "green": Pin(13, Pin.OUT),
    },
}


def turn_off(sem):
    for led in semaphores[sem].values():
        led.off()


def turn_on(sem, color):
    turn_off(sem)
    semaphores[sem][color].on()


# =========================
# WIFI AP MODE
# =========================
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(
    essid="ESP32",
    password="12345678",
    channel=6,
    authmode=network.AUTH_WPA_WPA2_PSK
)

print("IP:", ap.ifconfig()[0])

# =========================
# HTML UI (T1 → T6)
# =========================
html = """<!doctype html>
<html>
<head>
  <title>ESP32 Multi Semaphore</title>

  <style>
    body {
      margin: 0;
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #222;
      font-family: Arial;
    }

    .container {
      display: flex;
      gap: 30px;
      flex-wrap: wrap;
      justify-content: center;
    }

    .semaphore {
      background: #111;
      padding: 15px;
      border-radius: 20px;
      width: 100px;
      text-align: center;
      box-shadow: 0 0 15px rgba(0,0,0,0.8);
    }

    .title {
      color: white;
      margin-bottom: 10px;
      font-size: 14px;
      opacity: 0.7;
    }

    .light {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      margin: 10px auto;
      cursor: pointer;
      opacity: 0.4;
      transition: 0.3s;
    }

    .red { background: red; }
    .yellow { background: yellow; }
    .green { background: green; }

    .light:hover {
      opacity: 0.7;
      transform: scale(1.05);
    }

    .active.red {
      opacity: 1;
      box-shadow: 0 0 20px red, 0 0 50px red;
    }

    .active.yellow {
      opacity: 1;
      box-shadow: 0 0 20px yellow, 0 0 50px yellow;
    }

    .active.green {
      opacity: 1;
      box-shadow: 0 0 20px lime, 0 0 50px lime;
    }
  </style>
</head>

<body>

<div class="container">
"""

# Generate UI dynamically for T1 → T6
for i in range(1, 7):
    html += f"""
  <div class="semaphore">
    <div class="title">T{i}</div>
    <div id="T{i}_red" class="light red" onclick="setLight('T{i}','red')"></div>
    <div id="T{i}_yellow" class="light yellow" onclick="setLight('T{i}','yellow')"></div>
    <div id="T{i}_green" class="light green" onclick="setLight('T{i}','green')"></div>
  </div>
"""

html += """
</div>

<script>
function setLight(sem, color) {
  const el = document.getElementById(sem + "_" + color);

  // Toggle OFF
  if (el.classList.contains("active")) {
    fetch("/" + sem + "/off").catch(err => console.log(err));
    el.classList.remove("active");
    return;
  }

  // Turn ON
  fetch("/" + sem + "/" + color).catch(err => console.log(err));

  ["red","yellow","green"].forEach(c => {
    document.getElementById(sem + "_" + c).classList.remove("active");
  });

  el.classList.add("active");
}
</script>

</body>
</html>
"""

# =========================
# SERVER
# =========================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)

print("Server running...")

# =========================
# MAIN LOOP
# =========================
while True:
    client, addr = server.accept()
    request = client.recv(1024).decode()

    try:
        path = request.split(" ")[1]
        parts = path.strip("/").split("/")

        if len(parts) == 2:
            sem, action = parts

            if sem in semaphores:

                if action == "off":
                    turn_off(sem)

                    # Optional:
                    # If user turns semaphore OFF,
                    # train also stops
                    send_train_command("STOP")

                elif action == "red":
                    turn_on(sem, "red")
                    send_train_command("STOP")

                elif action == "yellow":
                    turn_on(sem, "yellow")
                    send_train_command("MEDIUM")

                elif action == "green":
                    turn_on(sem, "green")
                    send_train_command("FAST")
    except:
        pass

    client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    client.send(html)
    client.close()
