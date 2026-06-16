from machine import Pin, PWM
import time

ENA = PWM(Pin(19))
ENA.freq(1000)

INA1 = Pin(2, Pin.OUT)
INA2 = Pin(5, Pin.OUT)


INA1.on()
INA2.off()
while True:

    ENA.duty_u16(65535)
    print("led speed ")
    time.sleep(5)

    ENA.duty_u16(32767)
    print("led midume ")
    time.sleep(5)

    ENA.duty_u16(0)
    print("led zero ")
    time.sleep(5)
