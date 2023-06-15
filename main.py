import importlib
import subprocess
import sys 

def download_and_import(package_names):
    for package_name in package_names:
        try:
            importlib.import_module(package_name)
            print(f"{package_name} is already imported.")
        except ImportError:
            print(f"{package_name} is not imported. Downloading and importing...")
            try:
                subprocess.check_call(['pip', 'install', package_name])
            except subprocess.CalledProcessError as e:
                print(f"Failed to download or import {package_name}. Error: {e}. Try installing pip using: python -m pip install --upgrade pip")

required_packages = ['numpy', 'PyQt6', 'PyQt6.QtWidgets', 'pyqtgraph',  'serial']
imported_packages = download_and_import(required_packages)

import subprocess
import serial
import math
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)

grid_layout = QtWidgets.QGridLayout()

class WaveformGenerator(QtWidgets.QWidget):


    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waveform Generator')
        #test 
        grid_layout = QtWidgets.QGridLayout()
        # Initialize variables
        self.c1_fs = 1000
        self.c1_freq = 1
        self.c1_amplitude = 1
        self.c1_phase = 0
        self.c1_offset = 0
        self.c1_timeRange = 1
        self.dummy = 0
        self.waveform_type = 'sine'
        self.arbitrary_waveform = None
        self.toggled = 0
        #initialize default channel 2
        self.c2_fs = 1000
        self.c2_freq = 1
        self.c2_amplitude = 1
        self.c2_phase = 0
        self.c2_offset = 0
        self.c2_timeRange = 1
        self.c2_dummy = 0
        self.c2_waveform_type = 'sine'
        self.c2_arbitrary_waveform = None

        # Create GUI elements
        self.plot_widget = pg.PlotWidget()
        self.plot_widget2 = pg.PlotWidget()
        self.plot_data = self.plot_widget.plot(pen='y')
        self.c2_plot_data = self.plot_widget2.plot(pen='b')

        #initialize channel 1 inputs
        self.c1_label = QtWidgets.QLabel(f'Channel 1')
        self.freq_label = QtWidgets.QLabel(f'Frequency (Hz): {self.c1_freq}')
        self.freqSelect = QLineEdit()
        #self.freqSelect.resize(280,40) 
        self.amp_label = QtWidgets.QLabel(f'Amplitude: {self.c1_amplitude}')
        self.ampSelect = QLineEdit()
        #self.ampSelect.setValue(self.amplitude)
        self.offset_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.offset_label = QtWidgets.QLabel(f'Offset voltage: {self.c1_offset}')
        self.offset_slider.setRange(-5, 5)
        self.offset_slider.setValue(self.c1_offset)
        self.sine_button = QtWidgets.QPushButton('Sine')
        self.triangle_button = QtWidgets.QPushButton('Triangle')
        self.square_button = QtWidgets.QPushButton('Square')
        self.sawtooth_button = QtWidgets.QPushButton('Sawtooth')
        self.arb_button = QtWidgets.QPushButton('Arbitrary')
        self.arb_file_label = QtWidgets.QLabel('No file selected')
        self.arb_file_button = QtWidgets.QPushButton('Select file')
        self.generate_button = QtWidgets.QPushButton('Generate')

        #initialize channel 2 inputs
        self.c2_label = QtWidgets.QLabel(f'Channel 2')
        self.c2_freq_label = QtWidgets.QLabel(f'Frequency (Hz): {self.c2_freq}')
        self.c2_freqSelect = QLineEdit()
        #self.c2_freqSelect.resize(280, 40)
        self.c2_amp_label = QtWidgets.QLabel(f'Amplitude: {self.c2_amplitude}')
        self.c2_ampSelect = QLineEdit()


        # self.ampSelect.setValue(self.amplitude)
        self.c2_offset_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.c2_offset_label = QtWidgets.QLabel(f'Offset voltage: {self.c1_offset}')
        self.c2_offset_slider.setRange(-5, 5)
        self.c2_offset_slider.setValue(self.c1_offset)
        self.c2_sine_button = QtWidgets.QPushButton('Sine')
        self.c2_triangle_button = QtWidgets.QPushButton('Triangle')
        self.c2_square_button = QtWidgets.QPushButton('Square')
        self.c2_sawtooth_button = QtWidgets.QPushButton('Sawtooth')
        self.c2_arb_button = QtWidgets.QPushButton('Arbitrary')
        self.c2_arb_file_label = QtWidgets.QLabel('No file selected')
        self.c2_arb_file_button = QtWidgets.QPushButton('Select file')
        self.c2_generate_button = QtWidgets.QPushButton('Generate')

        self.toggle_button = QtWidgets.QPushButton('Split waveforms')
        #ErrorBox creation
        self.errorBox = QMessageBox()

        #Hardware restraints
        self.freqMin = 0
        self.freqMax = 14000000
        self.ampMin = 0
        self.ampMax = 5
        self.offsetMin = -5
        self.offsetMax = 5

        # Create layout
        grid_layout = QtWidgets.QGridLayout()

        grid_layout.addWidget(self.plot_widget, 0, 0, 8, 5)
        grid_layout.addWidget(self.c1_label, 0, 5, 1, 1)
        grid_layout.addWidget(self.freq_label, 1, 5, 1,1)
        grid_layout.addWidget(self.freqSelect, 1, 6)
        grid_layout.addWidget(self.amp_label, 2, 5)
        grid_layout.addWidget(self.ampSelect, 2, 6)
        grid_layout.addWidget(self.offset_label, 3, 5)
        grid_layout.addWidget(self.offset_slider, 3, 6)
        grid_layout.addWidget(self.sine_button, 4, 5,1,1)
        grid_layout.addWidget(self.triangle_button, 4, 6)
        grid_layout.addWidget(self.square_button, 5, 5)
        grid_layout.addWidget(self.sawtooth_button, 5, 6)
        grid_layout.addWidget(self.arb_button, 6, 5)
        grid_layout.addWidget(self.arb_file_label, 6, 6)
        grid_layout.addWidget(self.arb_file_button, 7, 6)
        grid_layout.addWidget(self.generate_button, 7, 5)

        grid_layout.addWidget(self.plot_widget2, 8, 0, 8, 5)
        grid_layout.addWidget(self.c2_label, 8, 5)
        grid_layout.addWidget(self.c2_freq_label, 9, 5)
        grid_layout.addWidget(self.c2_freqSelect, 9, 6)
        grid_layout.addWidget(self.c2_amp_label, 10, 5)
        grid_layout.addWidget(self.c2_ampSelect, 10, 6)
        grid_layout.addWidget(self.c2_offset_label, 11, 5)
        grid_layout.addWidget(self.c2_offset_slider, 11, 6)
        grid_layout.addWidget(self.c2_sine_button, 12, 5)
        grid_layout.addWidget(self.c2_triangle_button, 12, 6)
        grid_layout.addWidget(self.c2_square_button, 13, 5)
        grid_layout.addWidget(self.c2_sawtooth_button, 13, 6)
        grid_layout.addWidget(self.c2_arb_button, 14, 5)
        grid_layout.addWidget(self.c2_arb_file_label, 14, 6)
        grid_layout.addWidget(self.c2_arb_file_button, 15, 6)
        grid_layout.addWidget(self.c2_generate_button, 15, 5)

        #grid_layout.addWidget(self.toggle_button, 16, 5, 1, 2)
        self.setLayout(grid_layout)

        for i in range(0,6):
            grid_layout.setColumnStretch(i, 1)

        for i in range(0,16):
            grid_layout.setRowStretch(i, 1)
        
        # Connect signals to slots
        self.freqSelect.textChanged.connect(self.set_frequency)
        self.ampSelect.textChanged.connect(self.set_amplitude)
        self.offset_slider.valueChanged.connect(self.set_offset)
        self.sine_button.clicked.connect(self.set_sine)
        self.triangle_button.clicked.connect(self.set_triangle)
        self.square_button.clicked.connect(self.set_square)
        self.sawtooth_button.clicked.connect(self.set_sawtooth)
        self.arb_button.clicked.connect(self.set_arbitrary)
        self.arb_file_button.clicked.connect(self.select_arbitrary_file)
        self.generate_button.clicked.connect(self.generate_waveform)

        self.toggle_button.clicked.connect(self.toggleSplit)

        self.c2_freqSelect.textChanged.connect(self.set_c2_frequency)
        self.c2_ampSelect.textChanged.connect(self.set_c2_amplitude)
        self.c2_offset_slider.valueChanged.connect(self.set_c2_offset)
        self.c2_sine_button.clicked.connect(self.set_c2_sine)
        self.c2_triangle_button.clicked.connect(self.set_c2_triangle)
        self.c2_square_button.clicked.connect(self.set_c2_square)
        self.c2_sawtooth_button.clicked.connect(self.set_c2_sawtooth)
        self.c2_arb_button.clicked.connect(self.set_c2_arbitrary)
        self.c2_arb_file_button.clicked.connect(self.select_c2_arbitrary_file)
        self.c2_generate_button.clicked.connect(self.generate_c2_waveform)



    def set_frequency(self, value):
        self.c1_freq = value

    def set_c2_frequency(self, value):
        self.c2_freq = value

    def set_amplitude(self, value):
        self.c1_amplitude = value

    def set_c2_amplitude(self, value):
        self.c2_amplitude = value

    def parser(self,value):
        self.dummy = 1

    def c2_parser(self,value):
        self.c2_dummy = 1
    
    def set_offset(self, value):
        self.c1_offset = value

    def set_c2_offset(self, value):
        self.c2_offset = value

    def set_sine(self):
        self.waveform_type = 'sine'

    def set_c2_sine(self):
        self.c2_waveform_type = 'sine'

    def set_triangle(self):
        self.waveform_type = 'triangle'

    def set_c2_triangle(self):
        self.c2_waveform_type = 'triangle'

    def set_square(self):
        self.waveform_type = 'square'

    def set_c2_square(self):
        self.c2_waveform_type = 'square'

    def set_sawtooth(self):
        self.waveform_type = 'sawtooth'

    def set_c2_sawtooth(self):
        self.c2_waveform_type = 'sawtooth'

    def set_arbitrary(self):
        self.waveform_type = 'arbitrary'

    def set_c2_arbitrary(self):
        self.c2_waveform_type = 'arbitrary'

    def select_arbitrary_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('csv files (*.csv)')
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.arb_file_label.setText(file_path)
            self.arbitrary_waveform = np.loadtxt(file_path)

    def select_c2_arbitrary_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('csv files (*.csv)')
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.c2_arb_file_label.setText(file_path)
            self.c2_arbitrary_waveform = np.loadtxt(file_path)

    def load_arbitrary_waveform(self):
        try:
            # Read the CSV file and update the waveform data
            self.arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
            self.generate_waveform()
        except OSError:
            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')

    def load_c2_arbitrary_waveform(self):
        try:
            # Read the CSV file and update the waveform data
            self.c2_arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
            self.generate_waveform()
        except OSError:
            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')

    def generate_waveform(self):

        # Amplitude verification
        self.c1_amplitude = self.conversion(self.c1_amplitude, True)
        self.amp_label.setText(f'Amplitude: {self.c1_amplitude}')

        # Frequency verification
        self.c1_freq = self.conversion(self.c1_freq, False)
        self.freq_label.setText(f'Frequency (Hz): {self.c1_freq}')
        
        # Updating Data Visuals
        self.offset_label.setText(f'Offset voltage: {self.c1_offset}')
        
        self.c1_timeRange = pow(10, -(len(str(self.c1_freq))-1))
        print("Generate")
        print(type(self.c1_amplitude))
        print(type(self.c1_freq))
        print("Generate end.")
        if self.waveform_type == 'sine':
            t = np.linspace(0, self.c1_timeRange, self.c1_fs, endpoint=False)
            print(type(self.c1_freq))
            print(type(self.c1_amplitude))
            y = self.c1_amplitude * np.sin(2 * np.pi * self.c1_freq * t + np.deg2rad(self.c1_phase))+self.c1_offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'triangle':
            t = np.linspace(0, self.c1_timeRange, self.c1_fs, endpoint=False)
            y = self.c1_amplitude * (2 / np.pi * np.arcsin(np.sin(2 * np.pi * t * self.c1_freq + np.deg2rad(self.c1_phase))))+self.c1_offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'square':
            t = np.linspace(0, self.c1_timeRange, self.c1_fs, endpoint=False)
            y = self.c1_amplitude * np.where(np.mod(np.floor(2 * self.c1_freq * t + 2 * self.c1_phase / 360.0), 2) == 0, -1, 1)+self.c1_offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'sawtooth':
            t = np.linspace(0, self.c1_timeRange, self.c1_fs, endpoint=False)
            y = self.c1_amplitude * (2 / np.pi * np.arctan(np.tan(np.pi * t * self.c1_freq + np.deg2rad(self.c1_phase))))+self.c1_offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'arbitrary' and self.arbitrary_waveform is not None:
            t = np.linspace(0, self.c1_timeRange, len(self.arbitrary_waveform), endpoint=False)
            y = self.c1_amplitude * self.arbitrary_waveform+self.c1_offset
            self.plot_data.setData(t, y, pen='y')
        else:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')
        self.ampSelect.setText('')
        self.freqSelect.setText('')

    def generate_c2_waveform(self):

        # Amplitude verification
        self.c2_amplitude = (self.conversion(self.c2_amplitude, True))
        self.c2_amp_label.setText(f'Amplitude: {self.c2_amplitude}')
        

        # Frequency verification
        self.c2_freq = self.conversion(self.c2_freq, False)
        self.c2_freq_label.setText(f'Frequency (Hz): {self.c2_freq}')
        
        # Updating Data Visuals
        self.offset_label.setText(f'Offset voltage: {self.c2_offset}')
        
        self.c2_timeRange = pow(10, -(len(str(self.c2_freq))-1))

        # I have 0 idea why I have to cast amplitude to an int AGAIN for it to stay as an int
        print("Generate")
        print(type(self.c2_amplitude))
        print(type(self.c2_freq))
        print("Generate end.")
        if self.c2_waveform_type == 'sine':
            t = np.linspace(0, self.c2_timeRange, self.c2_fs, endpoint=False)
            y = self.c2_amplitude * np.sin(2 * np.pi * self.c2_freq * t + np.deg2rad(self.c2_phase))+self.c2_offset
            self.c2_plot_data.setData(t, y, pen='b')
        elif self.c2_waveform_type == 'triangle':
            t = np.linspace(0, self.c2_timeRange, self.c2_fs, endpoint=False)
            y = self.c2_amplitude * (2 / np.pi * np.arcsin(np.sin(2 * np.pi * t * self.c2_freq + np.deg2rad(self.c2_phase))))+self.c2_offset
            self.c2_plot_data.setData(t, y, pen='b')
        elif self.c2_waveform_type == 'square':
            t = np.linspace(0, self.c2_timeRange, self.c2_fs, endpoint=False)
            y = self.c2_amplitude * np.where(np.mod(np.floor(2 * self.c2_freq * t + 2 * self.c2_phase / 360.0), 2) == 0, -1, 1)+self.c2_offset
            self.c2_plot_data.setData(t, y, pen='b')
        elif self.c2_waveform_type == 'sawtooth':
            t = np.linspace(0, self.c2_timeRange, self.c2_fs, endpoint=False)
            y = self.c2_amplitude * (2 / np.pi * np.arctan(np.tan(np.pi * t * self.c2_freq + np.deg2rad(self.c2_phase))))+self.c2_offset
            self.c2_plot_data.setData(t, y, pen='b')
        elif self.c2_waveform_type == 'arbitrary' and self.c2_arbitrary_waveform is not None:
            t = np.linspace(0, self.c2_timeRange, len(self.c2_arbitrary_waveform), endpoint=False)
            y = self.c2_amplitude * self.c2_arbitrary_waveform+self.c2_offset
            self.c2_plot_data.setData(t, y, pen='b')
        else:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')
        #self.c2_ampSelect.setText('')
        #self.c2_freqSelect.setText('')



    def conversion(self, value, amplitude):
        suffixes = {'K': 1000, 'k': 1000, 'M': 1000000, 'm': 1000000}
        try:
            if isinstance(value, int): #This only passes if the value has not been changed
                return value
            if(len(value) == 1):
                return int(value)
            elif value[-1] in suffixes:
                multiplier = suffixes[value[-1]]
                answer = multiplier * int(value[:-1])
            else:
                answer = int(value)
            if (amplitude):
                if (int(value) >= self.ampMin) and (int(value) <= self.ampMax):
                    print("Valid Amplitude")
                    return int(answer)
                self.ThrowError("Amplitude must be between {0} and {1}".format(self.ampMin, self.ampMax))
            elif (int(value[:-1]) >= self.freqMin) and (int(value[:-1]) <= self.freqMax):
                print("Valid frequency")
                return int(answer)
            else:
                self.ThrowError("Frequency must be between {0}Hz and {1}MHz.".format(self.freqMin, int(self.freqMax/1000000)))
            return 0
        except:
            self.ThrowError("Invalid input(s).")
            return 0
        


    def toggleSplit(self):
        if(self.toggled == 0):
            #self.plot_widget.removeItem(self.c2_plot_data)
            grid_layout.removeWidget(self.plot_widget)
            #grid_layout.addWidget(self.plot_widget, 0, 0, 8, 4)
            grid_layout.update()
            #self.plot_widget2 = pg.PlotWidget()
            #self.addWidget(self.plot_widget, 0, 0, 17, 4)
            #self.addWidget()
            #grid_layout.addWidget(self.plot_widget, 0, 0, 17, 4)
            
    def compressWave(self,signal):
        self.dummy = 1

    #This function sends the entire array, no data loss. Handshake marker included for each element
    def  transferWave(self, signal,  ser, samplesize):
        try:
            # Convert the frequency value to a byte string and send it over serial port
            #freq_bytes = bytes(c1_fs, 'utf-8')
            ser.write(b'\x02') # start handshake packet
            for data in signal:

                print(f"Sending frequency: {data}")
                ser.write(data.encode())
                print("Sending")
                response = ser.read(2)
                print(f"Received response: {response}")

                # Testing values sent/received back
                freq_received = int.from_bytes(response, byteorder='little')
                print("Received frequency:", freq_received)

                #ser.flushInput()
                #ser.flushOutput() 

            ser.write(b'\x03') #End handshake packet
        except serial.SerialException:
            print('Failed to communicate with the device')
    
    def save_waveform(self):
        file_dialog = QtGui.QFileDialog()
        file_dialog.setDefaultSuffix('txt')
        file_dialog.setNameFilter('Text files (*.txt)')
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            t, y = self.plot_data.getData()
            np.savetxt(file_path, y)

    def reset_waveform(self):
        self.freq_slider.setValue(10)
        self.amp_slider.setValue(1)
        self.phase_slider.setValue(0)
        self.sine_button.setChecked(True)
        self.arb_file_label.setText('No file selected')
        self.arbitrary_waveform = None
        self.plot_data.clear()

    def ThrowError(self, message):
        self.errorBox.setText(message)
        self.errorBox.exec()
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    waveform_generator = WaveformGenerator()
    waveform_generator.show()
    sys.exit(app.exec())