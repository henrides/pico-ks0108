from machine import Pin
from KS0108 import ks0108
import random
import time

data = [Pin(0), Pin(1), Pin(2), Pin(3), Pin(4), Pin(5), Pin(6), Pin(7)]

lcd = ks0108(128, 64, Pin(12, Pin.OUT), [Pin(10), Pin(11)], Pin(9), Pin(8), Pin(13), data)
lcd.init_display()
print("LCD Init")

while True:
    x = random.randint(0, 63)
    y = random.randint(0, 55)
    lcd.fill(0)
    lcd.text("Bonjour", x, y)
    lcd.write_framebuffer()
    time.sleep(2)