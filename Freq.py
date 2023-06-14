import serial
import numpy

def feeler(ser):
    while True:
        # Prompt the user to input a frequency value
        freq_str = input("Enter frequency value (Hz) or 'q' to quit: ")

        if freq_str.lower() == 'q':
            break

        # Check if the input is a valid integer
        try:
            #freq = int(freq_str)
            print("Begin Test")
        except ValueError:
            print("Invalid input")
            continue

        # Send the frequency value to the STM32 over serial port
        send_freq(ser, freq_str)


def send_freq(ser, freq):
    try:
        # Convert the frequency value to a byte string and send it over serial port
        #freq_bytes = bytes(freq, 'utf-8')
        print(f"Sending frequency: {freq}")
        ser.write(freq.encode())
        print("Sending")
        response = ser.read(2)
        print(f"Received response: {response}")
        # Convert the received bytes to an integer value
        freq_received = int.from_bytes(response, byteorder='little')

        # Print the received frequency value
        print("Received frequency:", freq_received)

    except serial.SerialException:
        print('Failed to communicate with the device')


if __name__ == '__main__':
    try:
        ser = serial.Serial('COM3', 115200, timeout=1)
        feeler(ser)
    except serial.SerialException:
        print('Failed to open serial port')
    finally:
        ser.close()