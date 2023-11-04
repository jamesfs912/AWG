import serial
import serial.tools.list_ports
import threading
import math
from wavegen import *
from struct import pack
import os
from queue import Queue
import time 
from PyQt6.QtCore import pyqtSignal

def getSkips(freq, numSamples, fclk):
    return fclk / (freq * numSamples)

def error(f_target, skips, fclk, samples):
    skips = round(skips)
    fs = fclk / skips
    fo = fs / samples
    return abs((fo - f_target) / f_target) * 100
    
class Connection:
        
    def sendHandShakePacket(self):
        if self.status == "disconnected":
            return
        print("sending handshake packet")
        bytes = pack("B4B59x", 0, ord('I'), ord('N'), ord('I'), ord('T'))
        assert len(bytes) == 64
        self.sendQ.put(bytes)
        
    def read_disconnect(self, msg):
        if self.status != "disconnected":
            self.status = "disconnected"
            self.statusCallback.emit("disconnected", msg)
            self.ser.close()
                    
    def read_funct(self):
        timeouts = 0
        while self.status != "disconnected":
            try:
                buff = self.ser.read(64)
            except:
                buff = None
                self.read_disconnect("Connection Disconnected")
                break
                
            if len(buff) == 0: #timeout 
                #send keep alive packets?
                if timeouts == 0:
                    timeouts = 1
                    self.sendHandShakePacket()
                else:
                    print("timeut")
                    self.read_disconnect("timeout")
                pass
            else:
                if(buff[0:9] == bytes("\0STMAWG23", "ascii")):
                    timeouts = 0
                    if self.status == "connecting":
                        self.statusCallback.emit("connected", None)
                    self.status = "connected"
                    print("got ack")
                    #self.gotAck = True
                else:
                    self.status = "disconnected"
                    self.sendQ.put(None)
                    self.statusCallback.emit("disconnected", "Bad packet")
        self.sendQ.put(None)
        print("read close")
                
            
    def write_funct(self):
        while self.status != "disconnected":
            packet = self.sendQ.get()
            if packet:
                try:
                    self.ser.write(packet)
                except:
                    pass
        print("write close")
        
    def close(self):
        if self.status != "disconnected":
            self.status = "disconnected"
            self.ser.close()

    def up64(self, bytes):
        while(len(bytes) % 64 != 0):
            bytes += [0]
        return bytes
        
    def sendWave(self, chan, freq = 1e3, wave_type = "sin", amplitude = 5, offset = 0, arbitrary_waveform = None, duty = 50, phase = 0, forceGain = -1):
        if self.status == "disconnected":
            return
    
        #move constants to init or something
        fclk = 72e6
        dac_bits = 12
        pwm_bits = 12
        offset_amp = 5
        PWM_ARR = 2**pwm_bits - 1
        gain_amp = [5, 0.5]
    
        #which gain to use?
        #print(amplitude)        
        if forceGain == -1:
            if wave_type == "dc":
                gain = 0
            else:
                gain = 0 if abs(amplitude) > 0.5 else 1
        else:
            gain = forceGain
			
        #calculate offset CCR value
        offset_pwm = max(min(offset, 5), -5)
        CCR_offset = max(min(math.floor((-offset_pwm + offset_amp) / (offset_amp * 2) * PWM_ARR), PWM_ARR), 0)
        offset_dac = offset - offset_pwm
        
        #calculate number of samples to use, and the optimal sample period (skips)
        if wave_type == "dc": 
            numSamples = 2
            freq = 1e2
        else:
            skipGoal = 25
            max_samples = 1024*4
            numSamples = max_samples
            while (skips := getSkips(freq, numSamples, fclk)) < skipGoal:     
                #print(f"numSamples : {numSamples} skips: {skips}")
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
       # print("asd ", fclk / numSamples / skips_act)
        #calculate samples 
        dac_scale = (2**dac_bits) / 2
        
        phase_clocks = numSamples * (ARR + 1) * phase
        phase_samples = phase_clocks / (ARR + 1) / numSamples
        phase_arr = 0
        if chan == 1:
            pass
            #phase_arr += 6 // (PSC + 1)
        ##if PSC == 0:
        ##    phase_arr += int(phase_clocks) 
        #phase_arr += int(phase_clocks / (PSC + 1)) 
        
        #phase_arr += ARR
        phase_arr = phase_arr % (ARR + 1)
        
        
        print(phase, phase_clocks, phase_samples, phase_arr)
        
        samples = generateSamples(type = wave_type, numSamples = numSamples, amplitude = amplitude / gain_amp[gain] * dac_scale, arbitrary_waveform = arbitrary_waveform, duty = duty, phase = phase_samples, offset = dac_scale + offset_dac / gain_amp[gain] * dac_scale, clamp = [0, 2**dac_bits - 1])
        samples = samples[2]
        
        print(f"CCR_offset : {CCR_offset} gain_amp: {gain_amp[gain]}")
        print(f"numSamples : {numSamples} skips opt: {skips}")
        print(f"PSC : {PSC} ARR: {ARR}, skips act: {skips_act}")
        print(f"error skips_opt: {error(freq, skips, fclk, numSamples)}%")     
        print(f"error skips_act: {error(freq, skips_act, fclk, numSamples)}%")     
        
        bytes = pack("<BBBHHHHH51x", 1, chan, gain, PSC, ARR, CCR_offset, numSamples, phase_arr)
        sample_bytes = samplesToBytes(samples)
        assert len(bytes) % 64 == 0
        bytes += sample_bytes
        self.sendQ.put(bytes)
        
    def tryConnect(self):
        if self.status != "disconnected":
            return
            
        portName = None
    
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
            if(port.vid == 1155 and port.pid == 22336):
                portName = port.name
                break
			
        if not portName:
            self.statusCallback.emit("disconnected", "device not found")
            return
            
        if os.name == "posix":
            portName = "/dev/" + portName
            
        try:
            self.ser = serial.Serial(portName, 500000, timeout = 5) #BAUD Doesnt matter
        except Exception as e:
            print(e)
            self.statusCallback.emit("disconnected", "unable to open port")
            return
        
        self.status = "connecting"
        
        self.sendQ = Queue()
        self.sendHandShakePacket()
        
        self.write_thread = threading.Thread(target=self.write_funct, args=())
        self.write_thread.start()
        #
        self.read_thread = threading.Thread(target=self.read_funct, args=())
        self.read_thread.start()
        
    def __init__(self, statusCallback):
        self.status = "disconnected"
        self.statusCallback = statusCallback