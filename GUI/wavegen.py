import numpy as np

def generateSamples(type, numSamples, amplitude, offset = 0, timeRange = 1, arbitrary_waveform = None):
    if type == 'arbitrary':
        if arbitrary_waveform:
            t = np.linspace(0, 1, len(arbitrary_waveform), endpoint=False)
            y = arbitrary_waveform
        else:
            return (True, None, None) #indicate error
    else:
        t = np.linspace(0, 1, numSamples, endpoint=False)
        tt = t
        # + np.deg2rad(self.c1_phase) TODO: add phase back in
        #when adding phase do it by "rotating" t:
        #t = (t + phaseAs0to1) mod 1
    
        if type == 'sine':
            y =  np.sin(2 * np.pi * t)
        elif type == "triangle":
            t = np.mod(t + 0.25, 1)
            y = (np.mod(t * 2, 1) * -(np.floor(t * 2) * 2 - 1) + np.floor(t * 2)) * 2 - 1
        elif type == "square":
            y = np.floor(t * 2) * 2 - 1
        elif type == "sawtooth":
            t = np.mod(t + 0.5, 1)
            y = np.mod(t * 2, 2) - 1
        
    tt = tt * timeRange
    y = y * amplitude + offset
    return (False, tt, y)