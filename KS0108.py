from machine import Pin
import framebuf
import time

LCD_ON=0x3f
LCD_OFF=0x3e
LCD_DISPLAY_START=0xc0

class ks0108(framebuf.FrameBuffer):
    def __init__(self, width, height, e, cs, rs, rw, reset, data) -> None:
        self.width = width
        self.height = height

        self.pages = height // 8
        self.chips = width // 64

        self.e = e
        self.cs = cs
        self.rs = rs
        self.rw = rw
        self.data = data
        self.reset = reset

        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

    def init_display(self):
        self.e.init(Pin.OUT)
        self.rs.init(Pin.OUT)
        self.rw.init(Pin.OUT)
        for i in range(self.chips):
            self.cs[i].init(Pin.OUT)

        self.rs.low()
        self.rw.low()
        self.e.low()

        if self.reset != None:
            self.reset.init(Pin.OUT)
            self.reset.high()
            time.sleep_ms(1)
            self.reset.low()
            time.sleep_ms(1)
            self.reset.high()

        for i in range(self.chips):
            self.write_command(LCD_ON, i)
            self.write_command(LCD_DISPLAY_START, i)

        self.write_framebuffer()

    def write_command(self, cmd, chip):
        self.wait_ready(chip)
        self.set_data_direction(Pin.OUT)
        self.set_cs(chip)
        self.rs.low()
        self.rw.low()

        self.set_data_value(cmd)
        self.en()

    def write_data(self, data, chip):
        self.wait_ready(chip)
        self.set_data_direction(Pin.OUT)
        self.set_cs(chip)
        self.rs.high()
        self.rw.low()

        self.set_data_value(data)
        self.en()


    def wait_ready(self, chip):
        self.set_data_direction(Pin.IN)
        self.set_cs(chip)
        self.rs.low()
        self.rw.high()

        while True:
            self.en()
            if self.data[7].value() == 0 and self.data[4].value() == 0:
                break
            time.sleep_ms(1)

    def set_cs(self, chip):
        for i in range(self.chips):
            if i == chip:
                self.cs[i].high()
            else:
                self.cs[i].low()

    def set_data_direction(self, dir):
        for i in range(len(self.data)):
            self.data[i].init(dir, Pin.PULL_DOWN)

    def set_data_value(self, value):
        for i in range(8):
            val = (value >> i) & 0x01
            self.data[i].value(val)

    def en(self):
        time.sleep_us(1)
        self.e.high()
        time.sleep_us(1)
        self.e.low()

    def write_framebuffer(self):
        for page in range(self.pages):
            for chip in range(self.chips):
                addr = 0xb8 | (0x07 & page)
                self.write_command(addr, chip)
                self.write_command(0x40, chip)
                self.write_page(page, chip)
    
    def write_page(self, page, chip):
        for i in range(64):
            val = self.buffer[i + (64 * chip) + (page * self.width)]
            self.write_data(val, chip)
