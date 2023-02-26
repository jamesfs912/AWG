import numpy as np
import csv
import matplotlib.pyplot as plt

# Generate a sequence of time values with a time step of 0.01 seconds
t = np.arange(0, 1, 0.01)

# Generate a sine wave with frequency of 1 Hz and amplitude of 1
y = np.sin(2 * np.pi * t)

# Write the sine wave data to a CSV file
with open('sine_wave_graph.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(t)):
        writer.writerow([t[i], y[i]])

with open('sine_wave.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(t)):
        writer.writerow([y[i]])

# Plot the data as a graph
plt.plot(t, y)
plt.title('Sine Wave')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()
