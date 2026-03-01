import smbus
import time

DEVICE = 0x23
POWER_DOWN = 0x00
POWER_ON = 0x01
RESET = 0x07
CONTINUOUS_HIGH_RES_MODE_1 = 0x10

bus = smbus.SMBus(1)

def readLight(addr=DEVICE):
    bus.write_byte(addr, CONTINUOUS_HIGH_RES_MODE_1)
    time.sleep(0.2)
    data = bus.read_i2c_block_data(addr, CONTINUOUS_HIGH_RES_MODE_1, 2)
    
    return ((data[0] << 8) + data[1]) / 1.2

try:
    while True:
        lightLevel = readLight()
        print(f"Light Level: {lightLevel:.2f} lx")
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Measurement stopped.")
    