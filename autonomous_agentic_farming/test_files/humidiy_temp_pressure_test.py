#!/usr/bin/env python3
"""
BME280 Pressure + Temperature + Humidity — Raspberry Pi
Install: pip3 install adafruit-blinka adafruit-circuitpython-bme280
I2C Address: 0x76 (detected via i2cdetect)
Chip ID 0x60 = BME280 (includes humidity — better than BMP280)
"""

import csv
import os
import time
from datetime import datetime

import adafruit_bme280.basic as adafruit_bme280  # ✅ Changed from adafruit_bmp280
import board

# ── Config ────────────────────────────────────────────────────────────────────
I2C_ADDRESS = 0x76  # Confirmed from i2cdetect
SEA_LEVEL_PRESSURE = 1013.25  # hPa — adjust for local sea level
POLL_INTERVAL_S = 2
LOG_TO_CSV = True
LOG_FILE = "bme280_log.csv"

TEMP_WARN_HIGH = 35.0  # °C
PRESSURE_WARN_LOW = 980.0  # hPa


# ── Helpers ───────────────────────────────────────────────────────────────────
def classify_pressure(hpa: float) -> str:
    if hpa >= 1013:
        return "🔵 High pressure (fair weather)"
    if hpa >= 990:
        return "🟡 Normal"
    return "🟠 Low pressure (possible rain)"


def classify_humidity(rh: float) -> str:
    if rh < 30:
        return "🟠 Dry"
    if rh < 60:
        return "✅ Comfortable"
    return "🟡 Humid"


def init_csv(path: str):
    if not os.path.exists(path):  # noqa: PTH110
        with open(path, "w", newline="") as f:  # noqa: PTH123
            csv.writer(f).writerow(
                [
                    "timestamp",
                    "temperature_c",
                    "humidity_rh",
                    "pressure_hpa",
                    "altitude_m",
                ],
            )
        print(f"[LOG] Created: {path}")


def append_csv(path: str, temp: float, humidity: float, pressure: float, altitude: float):
    with open(path, "a", newline="") as f:  # noqa: PTH123
        csv.writer(f).writerow(
            [
                datetime.now().isoformat(),  # noqa: DTZ005
                f"{temp:.2f}",
                f"{humidity:.2f}",
                f"{pressure:.2f}",
                f"{altitude:.2f}",
            ],
        )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  BME280 Pressure + Temp + Humidity — Raspberry Pi")
    print("=" * 50)

    if LOG_TO_CSV:
        init_csv(LOG_FILE)

    i2c = board.I2C()
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=I2C_ADDRESS)  # ✅ Changed
    bme280.sea_level_pressure = SEA_LEVEL_PRESSURE

    print(f"[INFO] BME280 ready at I2C address 0x{I2C_ADDRESS:02X}")
    print(f"[INFO] Sea-level pressure reference: {SEA_LEVEL_PRESSURE} hPa")
    print("[INFO] Press Ctrl+C to stop.\n")

    try:
        while True:
            temperature = bme280.temperature  # °C
            humidity = bme280.humidity  # % RH  ✅ New — BME280 only
            pressure = bme280.pressure  # hPa
            altitude = bme280.altitude  # metres
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ005

            print(f"[{ts}]")
            print(f"  Temperature : {temperature:.2f} °C")
            print(f"  Humidity    : {humidity:.2f} % RH  — {classify_humidity(humidity)}")
            print(f"  Pressure    : {pressure:.2f} hPa   — {classify_pressure(pressure)}")
            print(f"  Altitude    : {altitude:.2f} m")
            print("-" * 50)

            if temperature >= TEMP_WARN_HIGH:
                print(f"  ⚠ WARNING: Temperature above {TEMP_WARN_HIGH}°C!")
            if pressure <= PRESSURE_WARN_LOW:
                print(f"  ⚠ WARNING: Pressure below {PRESSURE_WARN_LOW} hPa!")

            if LOG_TO_CSV:
                append_csv(LOG_FILE, temperature, humidity, pressure, altitude)

            time.sleep(POLL_INTERVAL_S)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped.")


if __name__ == "__main__":
    main()
