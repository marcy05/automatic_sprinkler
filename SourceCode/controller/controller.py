import machine
import utime
from umqtt.simple import MQTTClient
class Pump:
    def __init__(self, pump_id:int = 99, button_gpio:int = 99, red_gpio:int = 99, green_gpio:int = 99):
        self.pump_id: int = pump_id
        self._button_gpio: int = button_gpio
        self._red_gpio: int = red_gpio
        self._green_gpio: int = green_gpio

        self.button = machine.Pin(self._button_gpio, machine.Pin.IN, machine.Pin.PULL_UP)
        self.red = machine.Pin(self._red_gpio, machine.Pin.OUT)
        self.green = machine.Pin(self._green_gpio, machine.Pin.OUT)


# #### GLOBAL VARIABLE
p0 = Pump(0, 5, 28, 27)
p1 = Pump(1, 6, 26, 22)
p2 = Pump(2, 7, 21, 20)
p3 = Pump(3, 8, 19, 18)
p4 = Pump(4, 9, 17, 16)
p5 = Pump(5, 10, 12, 13)
p6 = Pump(6, 11, 14, 15)
pump_list = [p0, p1, p2, p3, p4, p5, p6]


def set_on_red():
    for pump in pump_list:
        pump.red.value(1)
    print("Set all red on")

def set_off_red():
    for pump in pump_list:
        pump.red.value(0)
    print("Set all red off")

def set_on_green():
    for pump in pump_list:
        pump.green.value(1)
    print("Set all green on")

def set_off_green():
    for pump in pump_list:
        pump.green.value(0)
    print("Set all green off")

def start_animation():
    print("Start animation")
    for pump in pump_list:
        pump.red.value(1)
        utime.sleep(.1)
        pump.red.value(0)
        pump.green.value(1)
        utime.sleep(.1)
        pump.green.value(0)

    print("Finish animation")

# ####  MAIN
set_off_green()
set_off_red()
start_animation()


while True:

    if not p0.button.value():
        p0.green.value(1)
        p0.red.value(1)
        utime.sleep(.5)
        p0.green.value(0)
        p0.red.value(0)
        utime.sleep(.5)
    if not p1.button.value():
        p1.green.value(1)
        p1.red.value(1)
        utime.sleep(.5)
        p1.green.value(0)
        p1.red.value(0)
        utime.sleep(.5)
    if not p2.button.value():
        p2.green.value(1)
        p2.red.value(1)
        utime.sleep(.5)
        p2.green.value(0)
        p2.red.value(0)
        utime.sleep(.5)
    if not p3.button.value():
        p3.green.value(1)
        p3.red.value(1)
        utime.sleep(.5)
        p3.green.value(0)
        p3.red.value(0)
        utime.sleep(.5)
    if not p4.button.value():
        p4.green.value(1)
        p4.red.value(1)
        utime.sleep(.5)
        p4.green.value(0)
        p4.red.value(0)
        utime.sleep(.5)
    if not p5.button.value():
        p5.green.value(1)
        p5.red.value(1)
        utime.sleep(.5)
        p5.green.value(0)
        p5.red.value(0)
        utime.sleep(.5)
    if not p6.button.value():
        p6.green.value(1)
        p6.red.value(1)
        utime.sleep(.5)
        p6.green.value(0)
        p6.red.value(0)
        utime.sleep(.5)
    utime.sleep(.2)