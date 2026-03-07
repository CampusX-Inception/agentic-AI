import time

import adafruit_bme280.basic as adafruit_bme280
import board
import neopixel
import smbus2 as smbus
from gpiozero import OutputDevice
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from scd30_i2c import SCD30

#### Hardware Setup  ####

# Water Pump (MOSFET on GPIO 26)
pump = OutputDevice(26)

# LED Strip (WS2812B on SPI pin GPIO 10)
PIXEL_PIN = board.D10
NUM_PIXELS = 10
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=0.2,
    auto_write=False,
    pixel_order=ORDER,
)

# BME280 — Temperature, Humidity, Pressure (I2C 0x76)
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# SCD30 — CO2 (I2C 0x61)
scd30 = SCD30()
scd30.set_measurement_interval(2)
scd30.start_periodic_measurement()

# BH1750 — Ambient Light (I2C 0x23)
bus = smbus.SMBus(1)
BH1750_ADDR = 0x23
BH1750_MODE = 0x10  # Continuous High-Res Mode 1

#### AI Tools  ####


@tool
def get_temperature_and_humidity() -> str:
    """Get the temperature in Celsius and humidity in percent from the BME280 sensor."""
    temperature = bme280.temperature
    humidity = bme280.humidity
    result = f"Temperature: {temperature:.1f} C, Humidity: {humidity:.1f}%"
    print(result)
    return result


@tool
def get_light() -> str:
    """Get the ambient light level in lux from the BH1750 sensor."""
    bus.write_byte(BH1750_ADDR, BH1750_MODE)
    time.sleep(0.2)
    data = bus.read_i2c_block_data(BH1750_ADDR, BH1750_MODE, 2)
    light = ((data[0] << 8) + data[1]) / 1.2
    result = f"Light: {light:.1f} lux"
    print(result)
    return result


@tool
def get_co2() -> str:
    """Get carbon dioxide level in ppm from the SCD30 sensor."""
    co2 = None
    if scd30.get_data_ready():
        measurement = scd30.read_measurement()
        if measurement is not None:
            co2 = measurement[0]
    result = f"CO2: {co2:.0f} ppm" if co2 is not None else "CO2: sensor not ready"
    print(result)
    return result


@tool
def turn_on_pump() -> str:
    """Turn on the water pump for 3 seconds to water the plants."""
    print("Action: Turning on pump")
    pump.on()
    time.sleep(3)
    pump.off()
    return "Pump watered the plants for 3 seconds"


@tool
def turn_on_lights(color: str) -> str:
    """Turn on the grow lights. color can be 'red', 'green', 'blue', or 'off'."""
    print(f"Action: Changing lights to {color}")

    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
    }
    rgb = colors.get(color.lower(), (0, 0, 0))

    for i in range(NUM_PIXELS):
        pixels[i] = rgb
        pixels.show()
        time.sleep(0.05)

    return f"Lights are now {color}"


#### Agent LLM protocol  ####

model = ChatOpenAI(
    api_key="PUT-YOUR-API-KEY-HERE",
    base_url="https://openrouter.ai/api/v1",
    model="qwen/qwen3-235b-a22b",
    temperature=0.2,
)

tools = [get_temperature_and_humidity, get_light, get_co2, turn_on_pump, turn_on_lights]

agent = create_agent(
    model.bind_tools(tools, parallel_tool_calls=False),
    tools,
    system_prompt="""You are an autonomous farming environment controller. Follow these rules strictly:

1. Always call get_temperature_and_humidity, get_light, and get_co2 first to take all sensor readings.
2. If humidity < 50%: call turn_on_pump to water the plants.
3. If light < 1000 lux: call turn_on_lights with 'red' or 'blue' to supplement grow lighting.
4. If light >= 1000 lux: call turn_on_lights with 'off' since natural light is sufficient.
5. If CO2 > 1000 ppm: mention that ventilation is recommended.
6. After acting, summarize all readings and actions taken.
7. When in doubt, do the first thing that comes to mind, don't overthink it.
""",
)

#### MAIN LOOP  ####

time.sleep(10)  # SCD30 warm-up

try:
    while True:
        print("\n" + "=" * 50)
        print("Invoking agent...")
        print("=" * 50)
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "Check all sensors, then act."}]},
        )
        print(result)
        time.sleep(60)

except KeyboardInterrupt:
    print("\nStopping...")
    pump.off()
    pixels.fill((0, 0, 0))
    pixels.show()
    scd30.stop_periodic_measurement()
    print("All hardware safely shut down.")
