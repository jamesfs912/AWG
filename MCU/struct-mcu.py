import serial
import struct
import time
import math

def create_packet1(sample_size, arr_value):
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
    serial_port.flush()
    response = serial_port.read(2)

    if len(response) == 2:
        response_data = struct.unpack('<H', response)[0]
        return response_data
    else:
        return None

def get_user_input():
    try:
        frequency = float(input("Enter desired frequency (Hz): "))
        num_samples = int(input("Enter number of samples: "))
        return frequency, num_samples
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None, None

def calculate_arr_value(frequency, num_samples):
    try:
        arr_value = int(48000000 / (frequency * num_samples))
        return arr_value
    except ZeroDivisionError:
        print("Error: Frequency and/or number of samples cannot be zero.")
        return None

def generate_sine_wave_lut(num_samples):
    try:
        lut_values = []
        for i in range(num_samples):
            angle = 2 * math.pi * i / num_samples
            sine_value = int((math.sin(angle) + 1) * 2047)  # Scale to 0-4095
            lut_values.append(sine_value)
        return lut_values
    except ZeroDivisionError:
        print("Error: Number of samples cannot be zero.")
        return None

def main():
    ser = serial.Serial('COM9', 115200)
    ser.close()
    ser.open()

    try:
        frequency, num_samples = get_user_input()
        if frequency is None or num_samples is None:
            return

        arr_value = calculate_arr_value(frequency, num_samples)
        if arr_value is None:
            return

        print(f"Sending ARR value: {arr_value}")
        print(f"Sending sample size: {num_samples}")

        packet1_data = create_packet1(num_samples, arr_value)
        time.sleep(1)
        response1 = send_and_receive_data(ser, packet1_data)
        if response1 is not None:
            print("Received response data:", response1)
        else:
            print("Received invalid response")

        lut_values = generate_sine_wave_lut(num_samples)
        if lut_values is not None:
            print("Generated LUT values:", lut_values)
            packet2_data = create_packet2(lut_values)
            time.sleep(1)
            response2 = send_and_receive_data(ser, packet2_data)
            if response2 is not None:
                print("Received response data:", response2)
            else:
                print("Received invalid response")

    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        ser.close()

if __name__ == "__main__":
    main()
