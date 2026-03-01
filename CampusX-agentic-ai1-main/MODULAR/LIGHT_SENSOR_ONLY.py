import smbus2 as smbus
import time
#import smbus: This imports the library that allows Python to talk to the "System Management Bus" (SMBus), which is essentially the I2C protocol. Without this, Python doesn't know how to send data out of the Pi's pins.
#import time: This gives us access to time-related functions, specifically time.sleep(), which we need to pause the program while the sensor is working.

# Constants
DEVICE     = 0x23  # Default device I2C address
POWER_DOWN = 0x00
POWER_ON   = 0x01
RESET      = 0x07
CONTINUOUS_HIGH_RES_MODE_1 = 0x10

#DEVICE = 0x23: This is the I2C Address of the BH1750. Think of it like a house number. When the Pi sends a message to "House 0x23", only the light sensor listens.
#POWER_DOWN / POWER_ON: These are commands found in the datasheet (the instruction manual) for the sensor. Sending 0x00 turns it off; 0x01 turns it on. https://erriez.github.io/ErriezBH1750/_erriez_b_h1750__regs_8h.html
#RESET = 0x07: This command wipes the sensor's data register to 0. It's useful to ensure you aren't reading old data.
#CONTINUOUS_HIGH_RES_MODE_1 = 0x10: This is the most important one.
      #Continuous: The sensor keeps measuring over and over.
      #High Res: It measures with high accuracy (1 lux).
      #Mode 1: It takes about 120ms to complete a measurement.
      #Why 0x10? The manufacturer decided that sending the binary number 00010000 (which is 0x10 in hex) tells the chip to enter this specific mode.


bus = smbus.SMBus(1)
#smbus.SMBus(1): This creates a connection to the physical pins on the Pi.
      #(1): This refers to I2C Bus 1.
      #Older Pis (very old Model 1s) used Bus 0.
      #All modern Pis (3, 4, 5, Zero) use Bus 1.

def readLight(addr=DEVICE):
    # Register the mode (this also powers it on)
    bus.write_byte(addr, CONTINUOUS_HIGH_RES_MODE_1)
    #bus.write_byte: This sends a command to the sensor.
    #addr: The house number (0x23).
    #CONTINUOUS...: The command (0x10).
    #Translation: "Hey device 0x23, please start measuring in High Res Mode."

    # Wait for sensor to measure (at least 120ms)
    time.sleep(0.2)

    # Read data (2 bytes)
    data = bus.read_i2c_block_data(addr, CONTINUOUS_HIGH_RES_MODE_1, 2)
    #read_i2c_block_data: This asks the sensor to send data back.
    #2: We ask for 2 bytes of data.
    #Why 2 bytes? The number can be up to 65,535. One byte (8 bits) only goes up to 255. So we need two bytes (16 bits) to hold the full number.

    # Convert 2 bytes into a number
    # Formula: (High Byte * 256 + Low Byte) / 1.2
    return ((data[0] << 8) + data[1]) / 1.2
    #calibration factor

try:
    while True:
        lightLevel = readLight()
        print(f"Light Level: {lightLevel:.2f} lx")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped")
