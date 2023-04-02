import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import csv
import tkinter.messagebox as messagebox

# Create a figure and axis for the waveform plot
fig, ax = plt.subplots()
ax.set_xlim([0, 1])
ax.set_ylim([-1, 1])
ax.set_title('Draw an Arbitrary Waveform')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')

# Initialize variables for storing the waveform data
t = []
y = []

# Initialize variables for tracking the drawing state
is_drawing = False

# Create a function to handle mouse clicks and motion on the waveform plot
def on_click(event):
    global is_drawing
    if event.button == 1:
        is_drawing = True
        x, yval = event.xdata, event.ydata
        t.append(x)
        y.append(yval)
        ax.plot(t, y, 'k')
        fig.canvas.draw()

def on_release(event):
    global is_drawing
    if event.button == 1:
        is_drawing = False
        if len(t) < 2:
            error_msg = 'Waveform must have at least two points'
            ax.set_title(error_msg, color='red')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            fig.canvas.draw()
            messagebox.showerror('Invalid waveform', 'Please close and try again!')
        elif t[-1] < t[-2]:
            error_msg = 'Waveform time values must be monotonically increasing'
            ax.set_title(error_msg, color='red')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            fig.canvas.draw()
            messagebox.showerror('Invalid waveform', 'Please close and try again!')
        else:
            ax.set_title('Waveform', color='black')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            fig.canvas.draw()

def on_motion(event):
    global is_drawing
    if is_drawing:
        x, yval = event.xdata, event.ydata
        if len(t) > 0 and x < t[-1]:
            x = t[-1]
        t.append(x)
        y.append(yval)
        ax.plot(t, y, 'k')
        fig.canvas.draw()

# Add a cursor to the waveform plot to help with drawing
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

# Add event listeners for mouse clicks and motion on the waveform plot
cid_click = fig.canvas.mpl_connect('button_press_event', on_click)
cid_release = fig.canvas.mpl_connect('button_release_event', on_release)
cid_motion = fig.canvas.mpl_connect('motion_notify_event', on_motion)

# Show the waveform plot and wait for the user to finish drawing
plt.show()

# Save the waveform data to a CSV file for plotting
with open('AWG_graph.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(t)):
        writer.writerow([t[i], y[i]])

# Save the waveform data to a CSV file for use with a waveform generator
with open('AWG.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(y)):
        writer.writerow([y[i]])
