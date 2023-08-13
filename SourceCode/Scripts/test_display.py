from machine import idle, Pin, SoftSPI
from src.display.ili9341 import Display, color565
from src.display.xpt2046 import Touch



class TouchDisplay:
    def __init__(self):
        self._sck = Pin(9)  # SCK bus can be the same for all SPI devices
        self._mosi = Pin(3)  # MOSI bus can be the same for all SPI devices
        self._miso = Pin(4)  # MISO bus can be the same for all SPI devices

        self._display_boudrate = 40000000
        self._dc_display = Pin(6)
        self._cs_display = Pin(5)
        self._rst_display = Pin(7)  # The parameter is mandatory, but you can connect it to VCC and set a random Pin

        self._touch_boudrate = 1000000
        self._cs_touch = Pin(9)
        self._irq_touch = Pin(0)

        self._spi1 = SoftSPI(baudrate=self._display_boudrate,
                             sck=self._sck,
                             mosi=self._mosi,
                             miso=self._miso)

        self._spi2 = SoftSPI(baudrate=self._touch_boudrate,
                             sck=self._sck,
                             mosi=self._mosi,
                             miso=self._miso)

        self.disp = Display(self._spi1, self._dc_display, self._cs_display, self._rst_display)
        self.touch = Touch(self._spi2, self._cs_touch, self._irq_touch, self.touchscreen_press)

    def print_raw_coord(self, x, y):
        print(f"Raw X: {x}, Raw Y: {y}")

    def touchscreen_press(self, x, y):
        """Process touchscreen press events."""
        # Y needs to be flipped
        # y = (self.display.height - 1) - y
        # !!! No more true. It is the X that has to be flipped
        x = (self.disp.width - 1) - x
        # Display coordinates
        self.disp.draw_text8x8(self.disp.width // 2 - 32,
                               self.disp.height - 9,
                               "{0:03d}, {1:03d}".format(x, y),
                               self.CYAN)
        print(f"X: {x}, Y: {y}")
        # Draw dot
        self.disp.draw_sprite(self.dot, x - 2, y - 2, 5, 5)

def main():

    touch_disp = TouchDisplay()
    print("Running")
    sem0 = False
    try:
        while True:
            if not sem0:
                print("Main loop")
                sem0 = True

            idle()
    except KeyboardInterrupt:
        print("\nCtrl-C pressed.  Cleaning up and exiting...")
    finally:
        touch_disp.disp.cleanup()



if __name__ == "__main__":
    main()
