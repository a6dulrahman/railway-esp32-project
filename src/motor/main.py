from machine import Pin, PWM
import network
import espnow
import time

ENA = PWM(Pin(19))
ENA.freq(1000)

INA1 = Pin(2, Pin.OUT)
INA2 = Pin(5, Pin.OUT)

INA1.on()
INA2.off()


STOP_SPEED = 0
MEDIUM_SPEED = 32767
FAST_SPEED = 65535

ENA.duty_u16(STOP_SPEED)


sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=6)

print("TRAIN ESP MAC:")
print(sta.config("mac"))


e = espnow.ESPNow()
e.active(True)

print("Waiting for commands...")


last_command = time.ticks_ms()


while True:

    host, msg = e.recv()

    if msg:

        last_command = time.ticks_ms()

        try:
            command = msg.decode()
        except:
            continue

        print("Received:", command)

        if command == "STOP":
            ENA.duty_u16(STOP_SPEED)

        elif command == "MEDIUM":
            ENA.duty_u16(MEDIUM_SPEED)

        elif command == "FAST":
            ENA.duty_u16(FAST_SPEED)

    if time.ticks_diff(time.ticks_ms(), last_command) > 5000:
        ENA.duty_u16(STOP_SPEED)
