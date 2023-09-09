# my_module.py

import serial
import struct
import time


def create_packet1(sample_size=30, arr_value=1600):
    packet1_id = 0x0101
    return struct.pack('<HHH', packet1_id, sample_size, arr_value)


def create_packet2(lut_values):
    packet2_id = 0x0202
    packet2_data = struct.pack('<H', packet2_id)
    for val in lut_values:
        packet2_data += struct.pack('<H', val)
    return packet2_data


def send_and_receive_data(serial_port, data):
    serial_port.write(data)
    response = serial_port.read(2)

    if len(response) == 2:
        response_data = struct.unpack('<H', response)[0]
        return response_data
    else:
        return None


def main():
    ser = serial.Serial('COM9', 115200)

    packet1_data = create_packet1()
    time.sleep(1)
    response1 = send_and_receive_data(ser, packet1_data)
    if response1 is not None:
        print("Received response data:", response1)
    else:
        print("Received invalid response")

    lut_values = [
        2048, 2473, 2880, 3251, 3569, 3821, 3995, 4084,
        4084, 3995, 3821, 3569, 3251, 2880, 2473, 2048,
        1622, 1215, 844, 526, 274, 100, 11, 11,
        100, 274, 526, 844, 1215, 1622, 204
    ]
    packet2_data = create_packet2(lut_values)
    time.sleep(1)
    response2 = send_and_receive_data(ser, packet2_data)
    if response2 is not None:
        print("Received response data:", response2)
    else:
        print("Received invalid response")


if __name__ == "__main__":
    main()

