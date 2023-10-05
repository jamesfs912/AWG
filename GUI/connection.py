import serial
import serial.tools.list_ports
import threading

class Connection:
    
    def read_funct():
        while True:
            buff = ser.read(64)
            if len(buff) == 0: #timeout
                self.connected = False
                self.statusCallback("disconnected")
            if(buff[0:9] == bytes("\0STMAWG23", "ascii")):
                self.statusCallback("connected")
                print("got ack")
                self.gotAck = True
            while self.gotAck:
                time.sleep(1/1000)
    
    def tryConnect(self):
        if self.connected:
            raise Exception("Shouldn't be here")
            return
            
        self.statusCallback("connecting")
        self.gotAck = False
    
        ports = list( serial.tools.list_ports.comports() )
        print("ports:")
        for port in ports:
            print("info:")
            print(port.name)
            print(port.description)
            print(port.hwid)
            print(port.vid)
            print(port.pid)
            print(port.serial_number)
            print(port.location)
            print(port.manufacturer)
            print(port.product)
            print(port.interface)
            print("\n")
            
        #TODO automaticly pick correct port given above
        com = "COM5"
        
        try:
            this.ser = serial.Serial(com, 500000, timeout = 1) #BAUD Doesnt matter
        except Exception as e:
            print(e)
            self.statusCallback("disconnected")
            return False
        
        self.recv_thread = threading.Thread(target=read_funct, args=())
        recv_thread.start()
        #send handshake here
    
    def __init__(self, statusCallback):
        self.connected = False
        self.gotAck = False
        self.statusCallback = statusCallback
        
#
#import time 
#import sys

#import math
#import random
#
#
##TODO use this to find the correct COM port?

#
##adds 0s to an array to make the size a multiple of 64
#def up64(bytes):
#	while(len(bytes) % 64 != 0):
#		bytes += [0]
#	return bytes
#

#
##add timeout fail mechanism
#def sendBytes(bytes):
#	global gotAck
#	gotAck = False
#	ser.write(bytes)
#	while not gotAck:
#		pass
#
#def sendHandShakePacket():
#	print("sending handshake packet")
#	bytes = [0] #packet type
#	for c in "INIT":
#		bytes += [ord(c)]
#	sendBytes(up64(bytes))
#
#		
#def sendConfigPacket(chan, freq, offset, size):
#	print("sending config packet")
#	bytes = [1] #packet type
#	bytes += [chan] #channel to configure
#	bytes += [freq]
#	bytes += [offset]
#	bytes += [size  & 0xFF, (size >> 8)  & 0xFF]
#	
#	bytes = up64(bytes)
#	if(size != 0):
#		if(size % 64 != 0):
#			print("BAD SIZE")
#				
#		checksum = 0
#		for i in range(size):
#			r = random.randint(0, 255)
#			checksum = (checksum + r) % 256;
#			bytes.append(r)
#		print("LUT checksum: ", checksum)
#	return sendBytes(bytes)
#
#time.sleep(0.01)
#t1 = threading.Thread(target=read_funct, args=())
#t1.start()
#
#	
#sendHandShakePacket()
#sendConfigPacket(0, 7, 4, 0)
#sendConfigPacket(1, 8, 5, 64)
#sendConfigPacket(0, 9, 6, 0)
#sendConfigPacket(1, 2, 3, 64 * 8)
#sendConfigPacket(1, 3, 3, 64 * 8)
#sendConfigPacket(1, 4, 3, 64 * 8)
#sendConfigPacket(1, 5, 3, 64 * 8)
#