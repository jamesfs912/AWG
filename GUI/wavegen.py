import numpy as np

def generateSamples(type, numSamples, amplitude, arbitrary_waveform = None, offset = 0, timeRange = 1, clamp = None):
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
    if clamp:
        np.clip(y, clamp[0], clamp[1], y)
    return (False, tt, y)
    
def samplesToBytes(samples):
    ns = len(samples)
    if ns % 64 != 0:
        add = 64 - (ns % 64)
        samples = np.pad(samples, (0,add), 'constant', constant_values=(0,))

    return samples.astype(dtype = "<u2", casting='unsafe').tobytes()