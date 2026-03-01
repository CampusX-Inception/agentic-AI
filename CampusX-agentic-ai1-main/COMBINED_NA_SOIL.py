import time
import board
import smbus2 as smbus
import neopixel
from gpiozero import OutputDevice
from scd30_i2c import SCD30
import adafruit_bme280.basic as adafruit_bme280


from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 1. Hardware Setup
# Pump
pump = OutputDevice(17)

# Lights
PIXEL_PIN = board.D10
NUM_PIXELS = 20
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=ORDER)

# BME280 (Temp, Humidity, Pressure)
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# SCD30 (CO2)
scd30 = SCD30()
scd30.set_measurement_interval(2)
scd30.start_periodic_measurement()

# Light Sensor (BH1750)
bus = smbus.SMBus(1)
DEVICE = 0x23
CONTINUOUS_HIGH_RES_MODE_1 = 0x10


# 2. Creating AI Tools using @tool syntax
@tool
def take_sensor_reading() -> str:
    """Take a sensor reading for temperature, humidity, CO2, and light."""
    # Read BME280
    temperature = bme280.temperature
    humidity = bme280.humidity

    # Read SCD30
    co2 = 0
    if scd30.get_data_ready():
        measurement = scd30.read_measurement()
        if measurement is not None:
            co2 = measurement[0]

    # Read Light Sensor
    bus.write_byte(DEVICE, CONTINUOUS_HIGH_RES_MODE_1)
    time.sleep(0.2)
    data = bus.read_i2c_block_data(DEVICE, CONTINUOUS_HIGH_RES_MODE_1, 2)
    light = ((data[0] << 8) + data[1]) / 1.2

    reading_result = f"Temp: {temperature:.1f}C, Hum: {humidity:.1f}%, CO2: {co2:.0f}ppm, Light: {light:.1f}lx"
    print(f"Sensor reading: {reading_result}")
    return reading_result

@tool
def turn_on_pump() -> str:
    """Turn on the pump for 3 seconds to water the plants."""
    print("\nAction: Turning on pump")
    pump.on()
    time.sleep(3)
    pump.off()
    return "Pump watered the plants"

@tool
def turn_on_lights(color_name: str) -> str:
    """Turn on the grow lights. color_name can be 'red', 'green', 'blue', or 'off'."""
    print(f"\nAction: Changing lights to {color_name}")

    if color_name.lower() == 'red':
        color = (255, 0, 0)
    elif color_name.lower() == 'green':
        color = (0, 255, 0)
    elif color_name.lower() == 'blue':
        color = (0, 0, 255)
    else:
        color = (0, 0, 0) # Off


    for i in range(NUM_PIXELS):
        pixels[i] = color
        pixels.show()
        time.sleep(0.05)

    return f"Lights are now {color_name}"


model = ChatOpenAI(
    api_key="put-api-key-here", #change this
    base_url="https://openrouter.ai/api/v1",
    model="qwen/qwen3-235b-a22b",
    temperature=0.2,
)

tools = [take_sensor_reading, turn_on_pump, turn_on_lights]

agent = create_agent(
    model.bind_tools(tools, parallel_tool_calls=False),
    tools,
    system_prompt="""You are an environment controller. Follow these rules strictly:
1. Always call take_sensor_reading first.
2. If humidity < 50: call turn_on_pump.
3. If light < 100: call turn_on_lights with 'red' or 'blue'.
4. If light >= 100: call turn_on_lights with 'off'.
5. when in doubt, do the first thing that comes to mind, don't overthink it.
"""
)


# 4. Continuous Running Loop
time.sleep(2) # Give sensors a brief moment to warm up

try:
    while True:
        agent.invoke({"messages": [{"role": "user", "content": "Check the sensor first, then act."}]})
        time.sleep(60) # Wait 60 seconds before next check

except KeyboardInterrupt:
    print("\nStopping...")
    # Safely turn everything off when quit
    pump.off()
    pixels.fill((0, 0, 0))
    pixels.show()
    scd30.stop_periodic_measurement()
