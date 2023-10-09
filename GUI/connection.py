import serial
import serial.tools.list_ports
import threading
import math
from wavegen import *
from struct import pack

def getSkips(freq, numSamples, fclk):
    return fclk / (freq * numSamples)

def error(f_target, skips, fclk, samples):
    skips = round(skips)
    fs = fclk / skips
    fo = fs / samples
    return abs((fo - f_target) / f_target) * 100
    
class Connection:
        
    def read_funct(self):
        #while True:
            #while self.gotAck:
            #    time.sleep(1/1000)
        buff = self.ser.read(64)
        if len(buff) == 0: #timeout
            self.connected = False
            self.statusCallback("disconnected")
            return
        if(buff[0:9] == bytes("\0STMAWG23", "ascii")):
            self.connected = True
            self.statusCallback("connected")
            print("got ack")
            #self.gotAck = True

    def up64(self, bytes):
        while(len(bytes) % 64 != 0):
            bytes += [0]
        return bytes
    

    
    def sendWave(self, chan, freq, wave_type, amplitude, offset, arbitrary_waveform = None):
        if False and not(self.connected):
            print("can't do this")
            #return
    
        #move constants to init or something
        fclk = 72e6
        dac_bits = 12
        pwm_bits = 12
        offset_amp = 5
        PWM_ARR = 2**pwm_bits - 1
        gain_amp = [5, 0.5]
    
        #which gain to use?
        print(amplitude)
        gain = 0 if amplitude > 0.5 else 1
              
        #calculate offset CCR value
        CCR_offset = max(min(math.floor((-offset + offset_amp) / (offset_amp * 2) * PWM_ARR), PWM_ARR), 0)
        
        #calculate number of samples to use, and the optimal sample period (skips)
        skipGoal = 20
        max_samples = 1024*4
        numSamples = max_samples
        while (skips := getSkips(freq, numSamples, fclk)) < skipGoal:     
            print(f"numSamples : {numSamples} skips: {skips}")
            numSamples /= 2
        skips = getSkips(freq, numSamples, fclk)
        numSamples = int(numSamples)
        
        #calculate PSC and ARR from the sample period (skips)
        PSC = 1
        while (ARR := skips / PSC) > 2**16:
            PSC += 1
        PSC -= 1
        ARR = round(ARR - 1)
        skips_act = (PSC+1)*(ARR+1)
        
        #calculate samples 
        dac_scale = (2**dac_bits) / 2
        samples = generateSamples(wave_type, numSamples, amplitude / gain_amp[gain] * dac_scale, arbitrary_waveform, dac_scale, clamp = [0, 2**dac_bits - 1])
        samples = samples[2]
        
        print(f"CCR_offset : {CCR_offset} gain_amp: {gain_amp[gain]}")
        print(f"numSamples : {numSamples} skips opt: {skips}")
        print(f"PSC : {PSC} ARR: {ARR}, skips act: {skips_act}")
        print(f"error skips_opt: {error(freq, skips, fclk, numSamples)}%")     
        print(f"error skips_act: {error(freq, skips_act, fclk, numSamples)}%")     
        bytes = pack("BBBBHHHH52x", 1, chan, 0, gain, PSC, ARR, CCR_offset, numSamples)
        sample_bytes = samplesToBytes(samples)
        assert len(bytes) % 64 == 0
        self.ser.write(bytes)
        self.ser.write(sample_bytes)
        self.read_funct()
    
    
    def sendHandShakePacket(self):
        print("sending handshake packet")
        #bytes = [0] #packet type
        #for c in "INIT":
        #    bytes += [ord(c)]
        #sendBytes(up64(bytes))
        bytes = pack("B4B59x", 0, ord('I'), ord('N'), ord('I'), ord('T'))
        assert len(bytes) == 64
        self.ser.write(bytes)
        self.read_funct()

    def tryConnect(self):
        if self.connected:
            print("Shouldn't be here")
            return
            
       # self.statusCallback("connecting")
        #self.gotAck = False
    
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
            self.ser = serial.Serial(com, 500000, timeout = 1) #BAUD Doesnt matter
        except Exception as e:
            print(e)
            self.statusCallback("disconnected", "unable to open port")
            return
        
        self.connected = True
        #recv_thread = threading.Thread(target=read_funct, args=())
        #recv_thread.start()
        self.sendHandShakePacket()
    
    def __init__(self, statusCallback):
        self.connected = False
        #self.gotAck = False
        self.statusCallback = statusCallback


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