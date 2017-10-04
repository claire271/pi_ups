#!/usr/bin/env python3

import wiringpi
import os
import sys
import time
import math

from gambezi_python import Gambezi

# Load config
filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.py")
exec(compile(open(filename, "rb").read(), filename, 'exec'))

print(GAMBEZI_SERVER_URL)

# Algorithm from https://www.3dbrew.org/wiki/CRC-8-CCITT
CRC_TABLE = [
    0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15, 0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D,
    0x70, 0x77, 0x7E, 0x79, 0x6C, 0x6B, 0x62, 0x65, 0x48, 0x4F, 0x46, 0x41, 0x54, 0x53, 0x5A, 0x5D,
    0xE0, 0xE7, 0xEE, 0xE9, 0xFC, 0xFB, 0xF2, 0xF5, 0xD8, 0xDF, 0xD6, 0xD1, 0xC4, 0xC3, 0xCA, 0xCD,
    0x90, 0x97, 0x9E, 0x99, 0x8C, 0x8B, 0x82, 0x85, 0xA8, 0xAF, 0xA6, 0xA1, 0xB4, 0xB3, 0xBA, 0xBD,
    0xC7, 0xC0, 0xC9, 0xCE, 0xDB, 0xDC, 0xD5, 0xD2, 0xFF, 0xF8, 0xF1, 0xF6, 0xE3, 0xE4, 0xED, 0xEA,
    0xB7, 0xB0, 0xB9, 0xBE, 0xAB, 0xAC, 0xA5, 0xA2, 0x8F, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9D, 0x9A,
    0x27, 0x20, 0x29, 0x2E, 0x3B, 0x3C, 0x35, 0x32, 0x1F, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0D, 0x0A,
    0x57, 0x50, 0x59, 0x5E, 0x4B, 0x4C, 0x45, 0x42, 0x6F, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7D, 0x7A,
    0x89, 0x8E, 0x87, 0x80, 0x95, 0x92, 0x9B, 0x9C, 0xB1, 0xB6, 0xBF, 0xB8, 0xAD, 0xAA, 0xA3, 0xA4,
    0xF9, 0xFE, 0xF7, 0xF0, 0xE5, 0xE2, 0xEB, 0xEC, 0xC1, 0xC6, 0xCF, 0xC8, 0xDD, 0xDA, 0xD3, 0xD4,
    0x69, 0x6E, 0x67, 0x60, 0x75, 0x72, 0x7B, 0x7C, 0x51, 0x56, 0x5F, 0x58, 0x4D, 0x4A, 0x43, 0x44,
    0x19, 0x1E, 0x17, 0x10, 0x05, 0x02, 0x0B, 0x0C, 0x21, 0x26, 0x2F, 0x28, 0x3D, 0x3A, 0x33, 0x34,
    0x4E, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5C, 0x5B, 0x76, 0x71, 0x78, 0x7F, 0x6A, 0x6D, 0x64, 0x63,
    0x3E, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2C, 0x2B, 0x06, 0x01, 0x08, 0x0F, 0x1A, 0x1D, 0x14, 0x13,
    0xAE, 0xA9, 0xA0, 0xA7, 0xB2, 0xB5, 0xBC, 0xBB, 0x96, 0x91, 0x98, 0x9F, 0x8A, 0x8D, 0x84, 0x83,
    0xDE, 0xD9, 0xD0, 0xD7, 0xC2, 0xC5, 0xCC, 0xCB, 0xE6, 0xE1, 0xE8, 0xEF, 0xFA, 0xFD, 0xF4, 0xF3]

def crc8ccitt(data, length):
    val = 0;
    index = 0

    while index < length:
        val = CRC_TABLE[val ^ data[index]]
        index += 1

    return val

# Can take data up to 254 bytes long
def cobs_stuff(data, length):
    index = 0
    count = 1

    while index + count < length:
        if data[index + count] == 0x00:
            data[index] = count
            index += count
            count = 1
        else:
            count += 1

    data[index] = count

# Can receive data up to 254 bytes long (excluding overhead)
def cobs_unstuff(data, length):
    index = 0

    while index < length:
        temp = index + data[index]
        data[index] = 0
        index = temp

    return (length > 0) and (length == index)

# Setup gambezi
print("Setting up Gambezi")
gambezi = Gambezi(GAMBEZI_SERVER_URL, True)
gambezi.set_refresh_rate(100)

node_red = gambezi.register_key(GAMBEZI_KEY + ['light', 'red'])
node_green = gambezi.register_key(GAMBEZI_KEY + ['light', 'green'])
node_blue = gambezi.register_key(GAMBEZI_KEY + ['light', 'blue'])
node_red.update_subscription(1)
node_green.update_subscription(1)
node_blue.update_subscription(1)

node_battery = gambezi.register_key(GAMBEZI_KEY + ['voltage', 'battery'])
node_external = gambezi.register_key(GAMBEZI_KEY + ['voltage', 'external'])
node_5volt = gambezi.register_key(GAMBEZI_KEY + ['voltage', '5 volt'])

node_current_out = gambezi.register_key(GAMBEZI_KEY + ['current', 'out'])
node_current_charge = gambezi.register_key(GAMBEZI_KEY + ['current', 'charge'])

node_state_power = gambezi.register_key(GAMBEZI_KEY + ['state', 'power'])
node_state_charge = gambezi.register_key(GAMBEZI_KEY + ['state', 'charge'])

# Setup I2C
print("Setting up I2C")
I2C = wiringpi.I2C()
fd = I2C.setupInterface(I2C_FILE, I2C_ADDRESS)

# Buffers
rx_length = 257
rx_index = 0
rx_buf = [0] * rx_length
tx_length = 257
tx_size = 0
tx_index = 0
tx_buf = [0] * tx_length

in_data = []
out_data = []

old_power_state = 0

try:
    print("Running main loop")

    while True:
        # Receive
        rx_buf[rx_index] = I2C.read(fd)
        if rx_buf[rx_index] == 0:
            if cobs_unstuff(rx_buf, rx_index):
                if crc8ccitt(rx_buf[1:], rx_index-1) == 0x00:
                    in_data = rx_buf[1: rx_index-1]

                    # Do something with the in data
                    if len(in_data) == 12:
                        # Process Pakcet
                        volt5_voltage = in_data[0] | (in_data[1] << 8)
                        volt5_voltage = volt5_voltage / 1023.0 * 16 * 1.1
                        external_voltage = in_data[2] | (in_data[3] << 8)
                        external_voltage = external_voltage / 1023.0 * 16 * 1.1
                        battery_voltage = in_data[4] | (in_data[5] << 8)
                        battery_voltage = battery_voltage / 1023.0 * 16 * 1.1
                        out_current = in_data[6] | (in_data[7] << 8)
                        out_current = out_current / 1023.0 * 1.1 / 2740 / 0.004 / 0.025
                        charge_current = in_data[8] | (in_data[9] << 8)
                        charge_current = charge_current / 1023.0 * 1.1 / 2740 / 0.004 / 0.100
                        power_state = in_data[10]
                        charge_state = in_data[11]

                        # Send data
                        node_battery.set_float(battery_voltage)
                        node_external.set_float(external_voltage)
                        node_5volt.set_float(volt5_voltage)
                        node_current_out.set_float(out_current)
                        node_current_charge.set_float(charge_current)
                        node_state_power.set_float(power_state)
                        node_state_charge.set_float(charge_state)

                        # Handle shutdown
                        if power_state == 2 and old_power_state == 1:
                            os.system("poweroff")
                        old_power_state = power_state
                    # End doing stuff with the in data

            rx_index = 0
        else:
            rx_index += 1
        rx_index %= rx_length
                    
        # Transmit
        I2C.write(fd, tx_buf[tx_index])
        tx_index += 1
        if tx_index >= tx_size:
            for i in range(0, len(out_data)):
                tx_buf[i+1] = out_data[i]
            tx_buf[len(out_data)+1] = crc8ccitt(out_data, len(out_data))
            cobs_stuff(tx_buf, len(out_data)+2)
            tx_buf[len(out_data)+2] = 0
            tx_size = len(out_data)+3
            tx_index = 0

            # Write something to out data
            out_data = [0] * 3
            red_value = node_red.get_float()
            green_value = node_green.get_float()
            blue_value = node_blue.get_float()
            out_data[0] = max(0, min(255, round(0 if math.isnan(red_value) else red_value)))
            out_data[1] = max(0, min(255, round(0 if math.isnan(green_value) else green_value)))
            out_data[2] = max(0, min(255, round(0 if math.isnan(blue_value) else blue_value)))
            # End write something to out data

        time.sleep(.002)
except BaseException as error:
    print(error)
finally:
    print("Exited")
