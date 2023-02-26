import numpy as np
import csv
import matplotlib.pyplot as plt

# Generate a sequence of time values with a time step of 0.01 seconds
t = np.arange(0, 1, 0.01)

# Generate a square wave with a frequency of 1 Hz and a duty cycle of 50%
y = np.where(np.mod(t, 1) < 0.5, 1, -1)

# Write the square wave data to a CSV file
with open('square_wave_graph.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(t)):
        writer.writerow([t[i], y[i]])

with open('square_wave.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(t)):
        writer.writerow([y[i]])

# Plot the data as a graph
plt.plot(t, y)
plt.title('Square Wave')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()
