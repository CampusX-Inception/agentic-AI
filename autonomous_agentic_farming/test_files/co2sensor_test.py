#!/usr/bin/env python3
"""
SCD-30 CO2 Sensor - Raspberry Pi Driver
Library: scd30-i2c  (pip3 install scd30-i2c)
This library is designed for direct Raspberry Pi GPIO I2C — no dongle needed.
"""

import csv
import os
import time
from datetime import datetime

from scd30_i2c import SCD30

# ── Config ────────────────────────────────────────────────────────────────────
MEASUREMENT_INTERVAL_S = 2  # Valid range: 2 to 1800 seconds
WARMUP_S = 10  # Stabilisation delay before first read
LOG_TO_CSV = True
LOG_FILE = "scd30_log.csv"
CO2_WARN_PPM = 1000
CO2_ALERT_PPM = 2000


# ── Helpers ───────────────────────────────────────────────────────────────────
def classify_co2(ppm: float) -> str:
    if ppm < 600:
        return "✅ Excellent"
    if ppm < 1000:
        return "🟡 Good"
    if ppm < 2000:
        return "🟠 Poor — Increase ventilation"
    return "🔴 Hazardous — Ventilate immediately"


def init_csv(path: str):
    if not os.path.exists(path):  # noqa: PTH110
        with open(path, "w", newline="") as f:  # noqa: PTH123
            csv.writer(f).writerow(["timestamp", "co2_ppm", "temperature_c", "humidity_rh"])
        print(f"[LOG] Created: {path}")


def append_csv(path: str, co2: float, temp: float, hum: float):
    with open(path, "a", newline="") as f:  # noqa: PTH123
        csv.writer(f).writerow(
            [
                datetime.now().isoformat(),  # noqa: DTZ005
                f"{co2:.0f}",
                f"{temp:.2f}",
                f"{hum:.2f}",
            ],
        )


def forced_recalibration(scd30: SCD30, reference_ppm: int = 400):
    """Run in fresh outdoor air (~400 ppm). Uncomment call in main() to use."""
    print("[CAL] Exposing sensor to reference air for 2 minutes...")
    time.sleep(120)
    scd30.forced_recalibration_with_reference(reference_ppm)
    print(f"[CAL] Done — reference set to {reference_ppm} ppm")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  SCD-30 CO2 Sensor — Raspberry Pi")
    print("=" * 50)

    if LOG_TO_CSV:
        init_csv(LOG_FILE)

    scd30 = SCD30()
    scd30.set_measurement_interval(MEASUREMENT_INTERVAL_S)
    scd30.start_periodic_measurement()

    print(f"[INFO] Warming up for {WARMUP_S}s — please wait...")
    time.sleep(WARMUP_S)
    print("[INFO] Ready. Press Ctrl+C to stop.\n")

    # Uncomment to run forced recalibration in fresh outdoor air:
    # forced_recalibration(scd30, reference_ppm=400)

    try:
        while True:
            if scd30.get_data_ready():
                measurement = scd30.read_measurement()

                if measurement is not None:
                    co2, temperature, humidity = measurement
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ005

                    print(f"[{ts}]")
                    print(f"  CO2         : {co2:.0f} ppm  — {classify_co2(co2)}")
                    print(f"  Temperature : {temperature:.2f} °C")
                    print(f"  Humidity    : {humidity:.2f} % RH")
                    print("-" * 50)

                    if co2 >= CO2_ALERT_PPM:
                        print(f"  ‼ ALERT: CO2 above {CO2_ALERT_PPM} ppm!")
                    elif co2 >= CO2_WARN_PPM:
                        print(f"  ⚠ WARNING: CO2 above {CO2_WARN_PPM} ppm")

                    if LOG_TO_CSV:
                        append_csv(LOG_FILE, co2, temperature, humidity)
                else:
                    print("[WARN] Measurement returned None — retrying...")
            else:
                print("[INFO] Waiting for data ready...")

            time.sleep(MEASUREMENT_INTERVAL_S)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
        scd30.stop_periodic_measurement()
        print("[INFO] Sensor stopped.")


if __name__ == "__main__":
    main()
