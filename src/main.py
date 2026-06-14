import network
import socket
from machine import Pin

# =========================
# LED SETUP (T1 → T4)
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
ap.config(essid="ESP32-Semaphores", password="12345678")

print("Connect to WiFi: ESP32-Semaphores")
print("IP:", ap.ifconfig()[0])

# =========================
# HTML UI (T1 → T4)
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
      gap: 40px;
      flex-wrap: wrap;
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
      width: 70px;
      height: 70px;
      border-radius: 50%;
      margin: 10px auto;
      cursor: pointer;
      opacity: 0.4;
      transition: all 0.3s ease;
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

  <div class="semaphore">
    <div class="title">T1</div>
    <div id="T1_red" class="light red" onclick="setLight('T1','red')"></div>
    <div id="T1_yellow" class="light yellow" onclick="setLight('T1','yellow')"></div>
    <div id="T1_green" class="light green" onclick="setLight('T1','green')"></div>
  </div>

  <div class="semaphore">
    <div class="title">T2</div>
    <div id="T2_red" class="light red" onclick="setLight('T2','red')"></div>
    <div id="T2_yellow" class="light yellow" onclick="setLight('T2','yellow')"></div>
    <div id="T2_green" class="light green" onclick="setLight('T2','green')"></div>
  </div>

  <div class="semaphore">
    <div class="title">T3</div>
    <div id="T3_red" class="light red" onclick="setLight('T3','red')"></div>
    <div id="T3_yellow" class="light yellow" onclick="setLight('T3','yellow')"></div>
    <div id="T3_green" class="light green" onclick="setLight('T3','green')"></div>
  </div>

  <div class="semaphore">
    <div class="title">T4</div>
    <div id="T4_red" class="light red" onclick="setLight('T4','red')"></div>
    <div id="T4_yellow" class="light yellow" onclick="setLight('T4','yellow')"></div>
    <div id="T4_green" class="light green" onclick="setLight('T4','green')"></div>
  </div>

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
        path = request.split(" ")[1]  # /T1/red
        parts = path.strip("/").split("/")

        if len(parts) == 2:
            sem, action = parts

            if sem in semaphores:
                if action == "off":
                    turn_off(sem)
                elif action in ["red", "yellow", "green"]:
                    turn_on(sem, action)
    except:
        pass

    client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    client.send(html)
    client.close()
