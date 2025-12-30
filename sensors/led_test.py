from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
import time

class LEDController:
    def __init__(self, spi_bus=0, spi_device=0, led_count=100):
        self.strip = WS2812SpiDriver(spi_bus=spi_bus, spi_device=spi_device, led_count=led_count).get_strip()

    def set_color(self, r, g, b):
        color = Color(r, g, b)
        self.strip.set_all_pixels(color)
        self.strip.show()

if __name__ == "__main__":

    # Initialize the WS2812 strip with 100 leds and SPI channel 0, CE0
    strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=100).get_strip()
    while True:
        strip.set_all_pixels(Color(255, 0, 0))
        strip.show()
        time.sleep(2)
        strip.set_all_pixels(Color(0, 255, 0))
        strip.show()
        time.sleep(2)
        strip.set_all_pixels(Color(0, 0, 255))
        strip.show()
        time.sleep(2)
