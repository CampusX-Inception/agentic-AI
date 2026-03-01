from gpiozero import OutputDevice
from time import sleep

# Define the pump
# GPIO 17 is Physical Pin 11
pump = OutputDevice(17)

def run_pump(seconds):
    print(f"Turning pump ON for {seconds} seconds...")
    pump.on()   # Turn on
    sleep(seconds)
    pump.off()  # Turn off
    print("Pump OFF.")

try:
    while True:
        user_input = input("Type 'run' to test pump (or 'q' to quit): ")

        if user_input.lower() == 'run':
            run_pump(3)  # Run for 3 seconds
        elif user_input.lower() == 'q':
            break

except KeyboardInterrupt:
    print("\nStopping...")
    pump.off()
