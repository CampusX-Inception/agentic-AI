import board
import neopixel
import time
 
# Configuration
# ON PI 5: Use board.SPI() or specify Pin 10 if using SPI method
# If standard GPIO 18 doesn't work, we use the SPI port (GPIO 10)
PIXEL_PIN = board.D10  
NUM_PIXELS = 20  # Change this to match your number of LEDs
ORDER = neopixel.GRB  # WS2812B is usually GRB, not RGB
 
# Create the pixel object
pixels = neopixel.NeoPixel(
    PIXEL_PIN, 
    NUM_PIXELS, 
    brightness=0.2, 
    auto_write=False,
    pixel_order=ORDER
)
 
def color_wipe(color, wait):
    """Wipe color across display a pixel at a time."""
    for i in range(NUM_PIXELS):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)
 
try:
    while True:
        print("Red")
        color_wipe((255, 0, 0), 0.05)  # Red
 
        print("Green")
        color_wipe((0, 255, 0), 0.05)  # Green
 
        print("Blue")
        color_wipe((0, 0, 255), 0.05)  # Blue
 
        print("Off")
        color_wipe((0, 0, 0), 0.01)    # Off
        time.sleep(1)
 
except KeyboardInterrupt:
    print("\nStopping...")
    pixels.fill((0, 0, 0))
    pixels.show()