import numpy as np
import csv
import matplotlib.pyplot as plt

# Generate a sequence of time values with a time step of 0.01 seconds
t = np.arange(0, 1, 0.01)

# Generate a triangle wave with a frequency of 1 Hz and amplitude of 1
y = np.abs(np.mod(t, 1) - 0.5) * 4 - 1

# Write the triangle wave data to a CSV file
with open('triangle_wave.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(t)):
        writer.writerow([y[i]])

# Plot the data as a graph
plt.plot(t, y)
plt.title('Triangle Wave')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()
