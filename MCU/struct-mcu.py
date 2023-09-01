import serial
import struct
import time

ser = serial.Serial('COM9', 115200)

arr_value = 3000
sample_size = 16
lut_values = [2048,2831,3495,3939,4095,3939,3495,2831,
2048,1264,600,156,0,156,600,1264]

data = struct.pack('<HH', sample_size, arr_value)
data += b''.join(struct.pack('<H', val) for val in lut_values)

time.sleep(1)

ser.write(data)

response = ser.read(2)

if len(response) == 2:
    response_data = struct.unpack('<H', response)[0]
    print("Received response data:", response_data)
else:
    print("Received invalid response:", response)

