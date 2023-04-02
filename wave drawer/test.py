from AWG.wave_drawer import WaveDrawer
import tkinter as tk


# Create a tkinter window
root = tk.Tk()

# Set the window title
root.title('Wave Drawer')

# Create a WaveDrawer
drawer = WaveDrawer(root)

# Start the tkinter event loop
root.mainloop()
