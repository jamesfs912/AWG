import serial

# Set up serial connection
ser = serial.Serial('COM6', 9600) # replace 'COM1' with the correct virtual COM port name

while True:
    # Read the frequency value from the console
    freq = input("Enter frequency: ")
    # Send the frequency value to the virtual COM port
    ser.write(freq.encode())