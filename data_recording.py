import numpy as np
import random
import sys
import serial
import csv
sys.path.append("..")
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

# UR3e com parameters
ROBOT_HOST = "192.168.56.20"
ROBOT_PORT = 30004
config_filename = "data_capture_config.xml"
# Output CSV file for recording data
OUTPUT_CSV_FILE = "recorded_data_03112023_78mm_soft.csv"
# Arduino serial connection parameters
ARDUINO_PORT = "COM4"  # Change to your Arduino's serial port
BAUD_RATE = 9600

logging.getLogger().setLevel(logging.INFO)

# Read configuration parameters from xml file
conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe("state")
setp_names, setp_types = conf.get_recipe("setp")

watchdog_names, watchdog_types = conf.get_recipe("watchdog") #CHECK

# Connect to the Arduino via serial
arduino_serial = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
# Number of positions recorded
num_samples = 300
# Generate range of values from the limits of each angle achievable
RY_range = np.linspace(-0.262, 0.262, 30)
RX_range = np.linspace(-0.262, 0.262, 30)
# crete meshgrid with all possible combinations
rx, ry = np.meshgrid(RX_range, RY_range)
# Flatten the meshgrid arrays
# rx = sorted(rx.flatten(), key=lambda x: random.random())
# ry = sorted(ry.flatten(), key=lambda x: random.random())
# Flatten the meshgrid arrays
rx_flat = rx.flatten()
ry_flat = ry.flatten()

# Combine flattened arrays into a list of (rx, ry) pairs
combined = list(zip(rx_flat, ry_flat))

# Shuffle the list randomly
random.shuffle(combined)

# Extract the first num_samples pairs as your selected data
selected_data = combined[:num_samples]

# If you need separate lists for rx and ry:
selected_rx, selected_ry = zip(*selected_data)
# Based on the numbers of samples select randomized samples
# selected_indices = random.sample(range(len(rx)), num_samples)

# Establish connection with UR robot
con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()
# get controller version
con.get_controller_version()

# setup recipes
con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

# Initialize variables
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0
sensor_measured = [0.0,0.0,0.0,0]
move_completed = True
j = 0
def read_sensor():
    i=0
    # Send the "R" command to request sensor data
    arduino_serial.write(b'R')
    # Read sensor measurements from Arduino via serial (assuming it sends 3 float values)
    while i<5:
        B = arduino_serial.readline().decode().strip()
        if B:
            sensor_data = [value for value in B.split(",")]
            print(sensor_data)
            return sensor_data
        i+=1
    if sensor_data ==['']:
        return [0,0,0]
# start data synchronization
if not con.send_start():
    sys.exit()

# Create a CSV file for recording data
with open(OUTPUT_CSV_FILE, "w", newline="") as csvfile:
    fieldnames = ["rx", "ry", "B_x", "B_y", "B_z"]
    data_recorded = csv.writer(csvfile,delimiter=",")
    data_recorded.writerow(fieldnames)
    # Measure sensor in the experiment home position
    sensor_measured = read_sensor()
    data_recorded.writerow([0,0,sensor_measured[0],sensor_measured[1],sensor_measured[2]])
    while True:
        # receive the current state
        state = con.receive()
        if state is None:
            break  
        if j < num_samples:
            # current_rx = rx[j]
            # current_ry = ry[j]
            if move_completed and state.output_int_register_0 == 1:
                move_completed = False
                # Send position
                setp.__dict__["input_double_register_%i" % 3] = selected_rx[j]
                setp.__dict__["input_double_register_%i" % 4] = selected_ry[j]
                con.send(setp)
                watchdog.input_int_register_0 = 1

            elif not move_completed and state.output_int_register_0==0:
                move_completed = True
                print("movement: ", j)
                # measure sensor
                sensor_measured = read_sensor()
                data_recorded.writerow([selected_rx[j],selected_ry[j],sensor_measured[0],sensor_measured[1],sensor_measured[2]])
                #next position
                j+=1
                watchdog.input_int_register_0 = 0

            
        con.send(watchdog)        
    con.send_pause()

    con.disconnect()