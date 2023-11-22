import serial
import serial.tools.list_ports
import threading
import math
from wavegen import *
from struct import pack
import os
from queue import Queue
import time 

class Connection:
        
    def sendHandShakePacket(self):
        """ Sends a handshake packet to the device.
        
        This function should be called when the device is first connected to."""
        if self.status == "disconnected":
            return
        bytes = pack("B4B59x", 0, ord('I'), ord('N'), ord('I'), ord('T'))
        assert len(bytes) == 64
        self.sendQ.put(bytes)
        
    def read_disconnect(self, msg):
        """ Disconnects the device and emits a disconnected signal.
        
        Parameters:
        msg (str): The reason for the disconnect.
        """
        if self.status != "disconnected":
            self.status = "disconnected"
            self.statusCallback.emit("disconnected", msg)
            self.ser.close()
                    
    def read_funct(self):
        """ The function that runs in the read thread. This function reads data from the serial port and emits signals when the device is connected or disconnected."""
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
                    self.read_disconnect("timeout")
                pass
            else:
                if(buff[0:9] == bytes("\0STMAWG23", "ascii")):
                    timeouts = 0
                    if self.status == "connecting":
                        self.statusCallback.emit("connected", None)
                    self.status = "connected"
                else:
                    self.status = "disconnected"
                    self.sendQ.put(None)
                    self.statusCallback.emit("disconnected", "Bad packet")
        self.sendQ.put(None)
            
    def write_funct(self):
        """ The function that runs in the write thread. This function writes data to the serial port."""
        while self.status != "disconnected":
            packet = self.sendQ.get()
            if packet:
                try:
                    self.ser.write(packet)
                except:
                    pass
        
    def close(self):
        """ Disconnects the device."""
        if self.status != "disconnected":
            self.status = "disconnected"
            self.ser.close()

    def up64(self, bytes):
        while(len(bytes) % 64 != 0):
            bytes += [0]
        return bytes
        
    def getSkips(self, freq, numSamples, fclk):
        return fclk / (freq * numSamples)
        
    def calc_val(self, freq):
        fclk = 72e6
        skipGoal = 25
        max_samples = 1024*4
        numSamples = max_samples
        while (skips := self.getSkips(freq, numSamples, fclk)) < skipGoal:     
            numSamples /= 2
            
        numSamples = int(numSamples)
        
         #calculate PSC and ARR from the sample period (skips)
        PSC = 1
        while (ARR := skips / PSC) > 2**16:
            PSC += 1
        PSC -= 1
        ARR = round(ARR - 1)
        
        return numSamples, ARR, PSC
        
        
    def sendWave(self, chan, freq = 1e3, wave_type = "sin", amplitude = 5, offset = 0, arbitrary_waveform = None, duty = 50, phase = 0, numPeriods = 1):
        """ Sends a waveform to the device.
        
        Parameters:
        chan (int): The channel to send the waveform to.
        freq (float): The frequency of the waveform.
        wave_type (str): The type of waveform to send.
        amplitude (float): The amplitude of the waveform.
        offset (float): The offset of the waveform.
        arbitrary_waveform (callable or None): A user-defined function for arbitrary waveforms, defaults to None.
        duty (int): Duty cycle for square waves, defaults to 50 percent.
        phase (float): Phase shift for the waveform, defaults to 0.
        numPeriods (int): Number of periods to generate, defaults to 1.
        """
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
        if wave_type == "dc" or offset > 5:
            gain = 0
        else:
            gain = 0 if abs(amplitude) > 0.5 else 1
        #calculate offset CCR value
        offset_pwm = max(min(offset, 5), -5)
        CCR_offset = max(min(math.floor((-offset_pwm + offset_amp) / (offset_amp * 2) * PWM_ARR), PWM_ARR), 0)
        offset_dac = offset - offset_pwm

        if wave_type == "dc": 
            numSamples, ARR, PSC = (2, int(2**15), 0)    
        else:
            numSamples, ARR, PSC = self.calc_val(freq)
        skips_act = (PSC+1)*(ARR+1)
        
        
        phase_clocks = numSamples * (ARR + 1) * phase
        phase_samples = phase_clocks / (ARR + 1) / numSamples
        phase_arr = 0
        if chan == 1:
            phase_arr += 6 // (PSC + 1)
        ##if PSC == 0:
        ##    phase_arr += int(phase_clocks) 
        phase_arr += int(phase_clocks / (PSC + 1)) 
        
        phase_arr = phase_arr % (ARR + 1)
        
        #print(phase, phase_clocks, phase_samples, phase_arr)
        dac_scale = (2**dac_bits) / 2
        samples = generateSamples(wavetype = wave_type, numSamples = numSamples, amplitude = amplitude / gain_amp[gain] * dac_scale, arbitrary_waveform = arbitrary_waveform, duty = duty, phase = phase_samples, offset = dac_scale + offset_dac / gain_amp[gain] * dac_scale, clamp = [0, 2**dac_bits - 1], numT = numPeriods)      
        samples = samples[1]

        bytes = pack("<BBBHHHHH51x", 1, chan, gain, PSC, ARR, CCR_offset, numSamples, phase_arr)
        sample_bytes = samplesToBytes(samples)
        assert len(bytes) % 64 == 0
        bytes += sample_bytes
        self.sendQ.put(bytes)
        
    def tryConnect(self):
        """ Attempts to connect to the device."""
        if self.status != "disconnected":
            return
            
        portName = None
    
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
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
        """ Initializes the connection object, setting it as disconnected."""
        self.status = "disconnected"
        self.statusCallback = statusCallback