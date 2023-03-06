import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import csv
import tkinter.messagebox as messagebox
import math


class WaveformDrawer:
    def __init__(self):
        # Create a figure and axis for the waveform plot
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim([-0.1, 1.1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_title('Draw an Arbitrary Waveform')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')

        # Initialize variables for storing the waveform data
        self.t = []
        self.y = []

        # Initialize variables for tracking the drawing state
        self.is_drawing = False

        # Add a cursor to the waveform plot to help with drawing
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)

    def draw_waveform(self):
        # Add event listeners for mouse clicks and motion on the waveform plot
        cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        # Show the waveform plot and wait for the user to finish drawing
        plt.show()

        # Remove event listeners for mouse clicks and motion on the waveform plot
        self.fig.canvas.mpl_disconnect(cid_click)
        self.fig.canvas.mpl_disconnect(cid_release)
        self.fig.canvas.mpl_disconnect(cid_motion)

    def on_click(self, event):
        if event.button == 1:
            self.is_drawing = True
            x, yval = event.xdata, event.ydata
            self.t.append(x)
            self.y.append(yval)
            self.ax.plot(self.t, self.y, 'k')
            self.fig.canvas.draw()

    def on_release(self, event):
        if event.button == 1:
            self.is_drawing = False
            if len(self.t) < 2:
                error_msg = 'Waveform must have at least two points'
                self.ax.set_title(error_msg, color='red')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Amplitude')
                self.fig.canvas.draw()
                messagebox.showerror('Invalid waveform', 'Please close and try again!')
            elif self.t[-1] < self.t[-2]:
                error_msg = 'Waveform time values must be monotonically increasing'
                self.ax.set_title(error_msg, color='red')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Amplitude')
                self.fig.canvas.draw()
                messagebox.showerror('Invalid waveform', 'Please close and try again!')
            else:
                self.ax.set_title('Waveform', color='black')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Amplitude')
                self.fig.canvas.draw()

    def on_motion(self, event):
        if self.is_drawing:
            x, yval = event.xdata, event.ydata
            if len(self.t) > 0 and x < self.t[-1]:
                x = self.t[-1]
            self.t.append(x)
            self.y.append(yval)
            self.ax.plot(self.t, self.y, 'k')
            self.fig.canvas.draw()

    def resample_waveform(self):
        # Resample the waveform to 128 samples and scale to a 12-bit DAC
        sample_rate = 128
        dac_range = 2 ** 12 - 1
        y_resampled = []
        for i in range(sample_rate):
            t_sample = i / sample_rate
            if t_sample > 1:
                break
            y_sample = 0
            for j in range(len(self.y)):
                if t_sample <= self.t[j]:
                    if j == 0:
                        y_sample = self.y[j]
                    else:
                        slope = (self.y[j] - self.y[j - 1]) / (self.t[j] - self.t[j - 1])
                        y_sample = slope * (t_sample - self.t[j - 1]) + self.y[j - 1]
                    break
            y_resampled.append(math.floor((y_sample + 1) * dac_range / 2))

        # Output the waveform to a CSV file
        with open('waveform.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for i in range(len(y_resampled)):
                writer.writerow([y_resampled[i]])

        # Print the waveform to the console
        for i in range(len(y_resampled)):
            if i % 12 == 0:
                print()
            if i == len(y_resampled) - 1:
                print(y_resampled[i], end="")
            else:
                print(y_resampled[i], end=", ")

        return y_resampled


waveform_drawer = WaveformDrawer()
waveform_drawer.draw_waveform()
resampled_waveform = waveform_drawer.resample_waveform()

