import numpy as np
from math import floor

def lerp(a, b, f):
    return a * (1 - f) + (b * f)

def resample(samples, newNumSamples):
    if len(samples) == newNumSamples:
        return samples
    values = []
    for i in range(newNumSamples):
        pos = i / newNumSamples * len(samples)
        ind = floor(pos)
        ind2 = (ind + 1) % len(samples)
        f = pos - ind
        
        #print(i, pos, ind, ind2, f)
        values += [lerp(samples[ind], samples[ind2], f)]
    return values
        

def generateSamples(type="sine", numSamples=1024, amplitude=5, arbitrary_waveform=None, duty=50, phase=0, offset=0,
                    timeRange=1, clamp=None, numT = 1):
                    
    t = np.linspace(0, numT, numSamples, endpoint=False)
                    
    if type == 'arbitrary':
        if arbitrary_waveform:
            t = np.linspace(0, 1, len(arbitrary_waveform), endpoint=False)
            y = arbitrary_waveform
            return (False, t, y)
        else:
            return (True, None, None)  # indicate error
    else:
        
        tt = t

        phase = float(phase)
        duty = float(duty)

        t = np.mod(t + phase, 1)

        if type == 'sine':
            y = np.sin(2 * np.pi * t)
        elif type == "triangle":
            t = np.mod(t + 0.25, 1)
            y = (np.mod(t * 2, 1) * -(np.floor(t * 2) * 2 - 1) + np.floor(t * 2)) * 2 - 1
        elif type == "square":
            y = np.ones(numSamples)
            y[t >= duty / 100] = -1
        elif type == "sawtooth":
            t = np.mod(t + 0.5, 1)
            y = np.mod(t * 2, 2) - 1
        elif type == "dc":
            y = np.zeros(numSamples)
        else:
            print("bad wavetype")

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