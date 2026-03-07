# Phase 1: System Prep & Core Drivers


# Update system packages and install necessary build tools
sudo apt update
sudo apt install -y swig python3-dev python3-setuptools git python3-rpi.gpio

# Clone and manually compile the lgpio library to fix missing module errors
cd ~
git clone https://github.com/joan2937/lg.git
cd lg
make
sudo make install

# Clean up the cloned installation folder
cd ~
rm -rf lg

# Enable the I2C and SPI interfaces
sudo raspi-config
# (Navigate to Interface Options -> I2C -> Yes)
# (Navigate to Interface Options -> SPI -> Yes)

# Reboot the Pi to apply the new interface settings (run this, then reconnect)
sudo reboot


# Phase 2: Unified Project Environment Setup


# Create the single project folder and enter it
mkdir ~/farmingfinal
cd ~/farmingfinal

# Create the virtual environment
python3 -m venv venv

# Activate the environment (You must run this command every time you open a new terminal)
source venv/bin/activate


# Phase 3: Install All Project Libraries


# Upgrade pip first
pip install --upgrade pip

# Install core GPIO, Pump/Relay, and general Sensor libraries
pip install rpi-lgpio gpiozero smbus2

# Install specific LED Strip libraries
pip install rpi_ws281x adafruit-circuitpython-neopixel

# Install the direct Raspberry Pi GPIO I2C library for the SCD-30
pip3 install scd30-i2c

# Install LangChain AI and LangGraph workflow libraries
pip install langchain langchain-openai langgraph


# Phase 4: Hardware Verification


# Verify that the SCD-30 and other I2C sensors are detected (SCD-30 should show as "61")
sudo i2cdetect -y 1

# (Save your python files inside ~/farmingfinal and run them like below)
# python3 scd30_sensor.py
