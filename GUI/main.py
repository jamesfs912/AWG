import importlib
import subprocess
import sys 
import os
import wave_drawer

## USB Modem, change data input type for offset, make a popup box for the device being connected, make the wave shape buttons generate instead of the generate button. Turn generate button into 
## a toggle channel off button. Change wave colors if it's off / illegal values. Generate when unfocused, Highlight shape chosen. Fix time base. Fix to one period. Sphynx documentation.
## Documentation : communication protocols
## Put a minimum size
## Batch, change color, fix offset changing
## Check if making a pip package is easier 
## Make it so sin is already selected 
## if both channels are the same frequency, enable a phase selector -German
## Add "DC" wave -German
## if square wave, enable duty cycle -German
## setting offset, amplitude, or frequency to decimal, such as "1.1" causes error -German
## make M = mega m = milli?, or both = milli? Mega makes sense for frequency but milli makes sense for amplitude/offset - German

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
					
#only do this if we are on windows	
if os.name == "nt":
	required_packages = ['numpy', 'PyQt6', 'pyqtgraph',  'serial']
	imported_packages = download_and_import(required_packages)
else:
	pass #handle macos/linux?

import subprocess
import math
import numpy as np
import pyqtgraph as pg
from connection import Connection
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,QComboBox
)
from wavegen import generateSamples

grid_layout = QtWidgets.QGridLayout()

class WaveformGenerator(QtWidgets.QWidget):
    statusCallbackSignal = pyqtSignal(str, str)

    def statusCallback(self, status, message):
        self.status_label.setText("Status: " + status)
        self.connectButton.setEnabled(status == "disconnected")
        if message:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', message)

    def connectButtonClicked(self):
        print("hello")
        self.connectButton.setEnabled(False)
        self.conn.tryConnect()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waveform Generator')

        grid_layout = QtWidgets.QGridLayout()

        # Create GUI elements
        self.plot_widget = pg.PlotWidget()
        self.plot_widget2 = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget2.setMouseEnabled(x=False, y=False)
        
        self.c1_guide_lines = []
        self.c2_guide_lines = []
        for i in range(3):
            self.c1_guide_lines.append(self.plot_widget.plot(pen=(255, 255, 0, 96)))
            self.c2_guide_lines.append(self.plot_widget2.plot(pen=(0, 255, 255, 96)))
            #self.c1_guide_lines.append(self.plot_widget.plot(pen=pg.mkPen(color='y', dash=[5, 5])))
            #self.c2_guide_lines.append(self.plot_widget2.plot(pen=pg.mkPen(color='c', dash=[5, 5])))
        
        
        self.plot_data = self.plot_widget.plot(pen='y')
        self.c2_plot_data = self.plot_widget2.plot(pen='b')

        self.init_dropdowns()
        self.init_restraints()
        self.init_values()
        self.init_inputs()
        self.init_layout()
        self.init_connections()
        
        self.statusCallbackSignal.connect(self.statusCallback)
        self.conn = Connection(self.statusCallbackSignal)
        self.connectButtonClicked()
        #self.conn.tryConnect()

    def init_values(self):
        self.GRAPH_SAMPLES = 1000
	
        # Initialize variables
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
        self.c2_freq = 1
        self.c2_amplitude = 1
        self.c2_phase = 0
        self.c2_offset = 0
        self.c2_timeRange = 1
        self.c2_dummy = 0
        self.c2_waveform_type = 'sine'
        self.c2_arbitrary_waveform = None

    def init_restraints(self):
        #Hardware restraints
        self.freqMin = 0
        self.freqMax = 1000000
        self.ampMin = 0
        self.ampMax = 5
        self.offsetMin = -5
        self.offsetMax = 5

    def init_inputs(self):
        self.status_label = QtWidgets.QLabel("Status: disconnected")
        self.connectButton = QtWidgets.QPushButton("Connect")
        self.connectButton.setEnabled(False)

        # initialize channel 1 inputs
        self.c1_label = QtWidgets.QLabel(f'Channel 1')
        self.freq_label = QtWidgets.QLabel(f'Frequency (Hz): {self.c1_freq}')
        self.freqSelect = QLineEdit()
        self.amp_label = QtWidgets.QLabel(f'Amplitude: {self.c1_amplitude}')
        self.ampSelect = QLineEdit()
        # self.offset_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.offset_label = QtWidgets.QLabel(f'Offset voltage: {self.c1_offset}')
        self.offsetSelect = QLineEdit()
        # self.offset_slider.setRange(-5, 5)
        # self.offset_slider.setValue(self.c1_offset)

        self.arb_file_label = QtWidgets.QLabel('No file selected')
        self.arb_file_button = QtWidgets.QPushButton('Select file')
        self.generate_button = QtWidgets.QPushButton('Generate')

        self.open_drawer = QtWidgets.QPushButton('open drawer')

        # initialize channel 2 inputs
        self.c2_label = QtWidgets.QLabel(f'Channel 2')
        self.c2_freq_label = QtWidgets.QLabel(f'Frequency (Hz): {self.c2_freq}')
        self.c2_freqSelect = QLineEdit()
        self.c2_amp_label = QtWidgets.QLabel(f'Amplitude: {self.c2_amplitude}')
        self.c2_ampSelect = QLineEdit()
        self.c2_offset_label = QtWidgets.QLabel(f'Offset voltage: {self.c1_offset}')
        self.c2_offset_select = QLineEdit()
        self.c2_arb_file_label = QtWidgets.QLabel('No file selected')
        self.c2_arb_file_button = QtWidgets.QPushButton('Select file')
        self.c2_generate_button = QtWidgets.QPushButton('Generate')

        self.errorBox = QMessageBox()
    
    def init_dropdowns(self):
        self.dropdown = QComboBox(self)
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')
        self.dropdown.addItem('Arbitrary')

        self.dropdown_c2 = QComboBox(self)
        self.dropdown_c2.addItem('Sine')
        self.dropdown_c2.addItem('Triangle')
        self.dropdown_c2.addItem('Sawtooth')
        self.dropdown_c2.addItem('Square')
        self.dropdown_c2.addItem('Arbitrary')
	
    def update_dropdown(self):
        self.waveform_type = self.dropdown.currentText().lower()

    def update_dropdown_c2(self):
        self.c2_waveform_type = self.dropdown_c2.currentText().lower()

    def init_layout(self):
        grid_layout = QtWidgets.QGridLayout()

        grid_layout.addWidget(self.status_label, 0, 0, 1, 1)
        grid_layout.addWidget(self.connectButton, 0, 1, 1, 1)

        grid_layout.addWidget(self.plot_widget, 1, 0, 8, 5)
        grid_layout.addWidget(self.c1_label, 1, 5, 1, 1)
        grid_layout.addWidget(self.freq_label, 2, 5, 1, 1)
        grid_layout.addWidget(self.freqSelect, 2, 6)
        grid_layout.addWidget(self.amp_label, 3, 5)
        grid_layout.addWidget(self.ampSelect, 3, 6)
        grid_layout.addWidget(self.offset_label, 4, 5)
        grid_layout.addWidget(self.offsetSelect, 4, 6)

        grid_layout.addWidget(self.dropdown, 5, 5, 1, 1)

        grid_layout.addWidget(self.arb_file_label, 5, 6)
        grid_layout.addWidget(self.arb_file_button, 6, 6)
        grid_layout.addWidget(self.generate_button, 6, 5)

        grid_layout.addWidget(self.open_drawer, 0, 3)

        grid_layout.addWidget(self.plot_widget2, 9, 0, 8, 5)
        grid_layout.addWidget(self.c2_label, 9, 5)
        grid_layout.addWidget(self.c2_freq_label, 10, 5)
        grid_layout.addWidget(self.c2_freqSelect, 10, 6)
        grid_layout.addWidget(self.c2_amp_label, 11, 5)
        grid_layout.addWidget(self.c2_ampSelect, 11, 6)
        grid_layout.addWidget(self.c2_offset_label, 12, 5)
        grid_layout.addWidget(self.c2_offset_select, 12, 6)

        grid_layout.addWidget(self.dropdown_c2, 13, 5, 1, 1)

        grid_layout.addWidget(self.c2_arb_file_label, 13, 6)
        grid_layout.addWidget(self.c2_arb_file_button, 14, 6)
        grid_layout.addWidget(self.c2_generate_button, 14, 5)

        self.setLayout(grid_layout)
        self.plot_widget.setLabel('left', text='', units='V')
        self.plot_widget.setLabel('bottom', text='', units='s')
        self.plot_widget.setYRange(-10, 10)
        self.plot_widget.setMinimumSize(600, 400)

        self.plot_widget2.setLabel('left', text='', units='V')
        self.plot_widget2.setLabel('bottom', text='', units='s')
        self.plot_widget2.setYRange(-10, 10)
        self.plot_widget2.setMinimumSize(600, 400)
        self.plot_widget2.setLabel('left', text='', units='V')
        self.plot_widget2.setLabel('bottom', text='', units='s')

        for i in range(1, 6):
            grid_layout.setColumnStretch(i, 1)

        for i in range(1, 17):
            grid_layout.setRowStretch(i, 1)

    def init_connections(self):
        self.connectButton.clicked.connect(self.connectButtonClicked)

        # Connect signals to slots
        self.freqSelect.textChanged.connect(self.set_frequency)
        self.ampSelect.textChanged.connect(self.set_amplitude)
        self.offsetSelect.textChanged.connect(self.set_offset)

        self.dropdown.activated.connect(lambda: self.update_dropdown())

        self.arb_file_button.clicked.connect(self.select_arbitrary_file)
        self.generate_button.clicked.connect(self.generate_waveform)

        self.open_drawer.clicked.connect(self.fun_open_drawer)

        # self.toggle_button.clicked.connect(self.toggleSplit)

        self.c2_freqSelect.textChanged.connect(self.set_c2_frequency)
        self.c2_ampSelect.textChanged.connect(self.set_c2_amplitude)
        self.c2_offset_select.textChanged.connect(self.set_c2_offset)

        self.dropdown_c2.activated.connect(lambda: self.update_dropdown_c2())

        self.c2_arb_file_button.clicked.connect(self.select_c2_arbitrary_file)
        self.c2_generate_button.clicked.connect(self.generate_c2_waveform)

    def fun_open_drawer(self):
        drawer_window.show()
        
    #The following functions set the frequency values based on the user input
    def set_frequency(self, value):
        self.c1_freq = value

    def set_c2_frequency(self, value):
        self.c2_freq = value

    #The following functions set the amplitude values based on the user input
    def set_amplitude(self, value):
        self.c1_amplitude = value

    def set_c2_amplitude(self, value):
        self.c2_amplitude = value

    # Need to verify with James what this is for
    def parser(self,value):
        self.dummy = 1

    def c2_parser(self,value):
        self.c2_dummy = 1
    
    # Note to self, add auto updating for the offset label.
    # The following instructions set the offet values based on the user input. Check with James if we need to do calculations on our end
    def set_offset(self, value):
        self.c1_offset = value

    def set_c2_offset(self, value):
        self.c2_offset = value

    # The following instructions set the non-AWG wave type
    def set_sine(self):
        self.set_Button_off()
        self.sine_button.setChecked(True)
        self.waveform_type = 'sine'

    def set_c2_sine(self):
        self.set_Button_off2()
        self.c2_sine_button.setChecked(True)
        self.c2_waveform_type = 'sine'

    def set_triangle(self):
        self.set_Button_off()
        self.triangle_button.setChecked(True)
        self.waveform_type = 'triangle'

    def set_c2_triangle(self):
        self.set_Button_off2()
        self.c2_triangle_button.setChecked(True)
        self.c2_waveform_type = 'triangle'

    def set_square(self):
        self.set_Button_off()
        self.square_button.setChecked(True)
        self.waveform_type = 'square'

    def set_c2_square(self):
        self.set_Button_off2()
        self.c2_square_button.setChecked(True)
        self.c2_waveform_type = 'square'

    def set_sawtooth(self):
        self.set_Button_off()
        self.sawtooth_button.setChecked(True)
        self.waveform_type = 'sawtooth'

    def set_c2_sawtooth(self):
        self.set_Button_off2()
        self.c2_sawtooth_button.setChecked(True)
        self.c2_waveform_type = 'sawtooth'

    def set_arbitrary(self):
        self.set_Button_off()
        self.arb_button.setChecked(True)
        self.waveform_type = 'arbitrary'

    def set_c2_arbitrary(self):
        self.set_Button_off2()
        self.c2_arb_button.setChecked(True)
        self.c2_waveform_type = 'arbitrary'

    # Takes the user inputted CSV files and loads them as the current waveform
    def select_arbitrary_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('csv files (*.csv)')
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.arb_file_label.setText(file_path)
            self.arbitrary_waveform = np.loadtxt(file_path)

    # Takes the user inputted CSV files and loads them as the current waveform
    def select_c2_arbitrary_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('csv files (*.csv)')
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.c2_arb_file_label.setText(file_path)
            self.c2_arbitrary_waveform = np.loadtxt(file_path)

    # Generates the waveform from the 
    def load_arbitrary_waveform(self):
        try:
            # Read the CSV file and update the waveform data
            self.arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
            self.generate_waveform()
        except OSError:
            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')

    # Generates the waveform from the file saved by the user. Note to Vik: You might have to change the filename to not conflict with c1 and c2
    def load_c2_arbitrary_waveform(self):
        try:
            # Read the CSV file and update the waveform data
            self.c2_arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
            self.generate_waveform()
        except OSError:
            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')
    
    # Generates the first waveform based on the user inputs
    def generate_waveform(self):
        # Amplitude verification
        self.c1_amplitude = self.amplitude_verification(self.c1_amplitude)
        self.amp_label.setText(f'Amplitude: {self.c1_amplitude}')
        #print(type(self.c1_amplitude))

        # Frequency verification
        self.c1_freq = self.freq_verification(self.c1_freq)
        self.freq_label.setText(f'Frequency (Hz): {self.c1_freq}')
        
        # Updating Data Visuals
        self.offset_label.setText(f'Offset voltage: {self.c1_offset}')
        self.c1_offset = self.offset_verification(self.c1_offset)
        
        # Sets the time base to always display at most 10 cycles.
        #self.c1_timeRange = pow(10, -(len(str(self.c1_freq))-1))

        #Different waveform generations based on waveform type
        tr = 1 / self.c1_freq
        samples = generateSamples(self.waveform_type, self.GRAPH_SAMPLES, self.c1_amplitude, self.arbitrary_waveform, offset = self.c1_offset, timeRange = tr)
        if samples[0]:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')
             
        self.plot_data.setData(samples[1], samples[2], pen='y')
        self.plot_widget.setLabel('left', text='', units='V')
        self.plot_widget.setLabel('bottom', text='', units= 's')
        self.plot_widget.setXRange(0, tr)
        self.c1_guide_lines[0].setData([-tr, tr * 2], [self.c1_offset, self.c1_offset])
        self.c1_guide_lines[1].setData([-tr, tr * 2], [self.c1_offset + self.c1_amplitude, self.c1_offset + self.c1_amplitude])
        self.c1_guide_lines[2].setData([-tr, tr * 2], [self.c1_offset - self.c1_amplitude, self.c1_offset - self.c1_amplitude])
        self.conn.sendWave(0, self.c1_freq, self.waveform_type, self.c1_amplitude, self.c1_offset, self.arbitrary_waveform)
        
     # Generates the second waveform based on the user inputs
    
    def generate_c2_waveform(self):
        # Amplitude verification
        self.c2_amplitude = self.amplitude_verification(self.c2_amplitude)
        self.c2_amp_label.setText(f'Amplitude: {self.c2_amplitude}')

        # Frequency verification
        self.c2_freq = self.freq_verification(self.c2_freq)
        self.c2_freq_label.setText(f'Frequency (Hz): {self.c2_freq}')
        
        # Updating Data Visuals
        self.c2_offset_label.setText(f'Offset voltage: {self.c2_offset}')
        self.c2_offset = self.offset_verification(self.c2_offset)
    
        tr = 1 / self.c2_freq
        samples = generateSamples(self.c2_waveform_type, self.GRAPH_SAMPLES, self.c2_amplitude, self.arbitrary_waveform, offset = self.c2_offset, timeRange = tr)
        if samples[0]:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')
            
        self.c2_plot_data.setData(samples[1], samples[2], pen='c')
        self.plot_widget2.setLabel('left', text='', units='V')
        self.plot_widget2.setLabel('bottom', text='', units='s')
        self.plot_widget2.setXRange(0, tr)
        self.c2_guide_lines[0].setData([-tr, tr * 2], [self.c2_offset, self.c2_offset])
        self.c2_guide_lines[1].setData([-tr, tr * 2], [self.c2_offset + self.c2_amplitude, self.c2_offset + self.c2_amplitude])
        self.c2_guide_lines[2].setData([-tr, tr * 2], [self.c2_offset - self.c2_amplitude, self.c2_offset - self.c2_amplitude])
        self.conn.sendWave(1, self.c2_freq, self.c2_waveform_type, self.c2_amplitude, self.c2_offset, self.arbitrary_waveform)

        #self.c2_ampSelect.setText('')
        #self.c2_freqSelect.setText('')

    def offset_verification(self, value):
        prefixes = {'m': 0.001, 'V': 1, 'v': 1, 'mV': 0.001, 'mv': 0.001}
        try:
            if isinstance(value, (int, float)):  # This only passes if the value is already numeric
                return value

            # prefix conversion
            if value[-2:] in prefixes:
                multiplier = prefixes[value[-2:]]
                answer = multiplier * float(value[:-2])
            elif value[-1] in prefixes:
                multiplier = prefixes[value[-1]]
                answer = multiplier * float(value[:-1])
            else:
                answer = float(value)
            if self.offsetMin <= answer <= self.offsetMax:
                return answer

            self.ThrowError("Voltage must be between {0}V and {1}V.".format(self.offsetMin, self.offsetMax))
            return 0
        
        except Exception as e:
            print(e)
            self.ThrowError("Invalid input(s). With value: " + value)
            return 0

    def amplitude_verification(self, value):
        prefixes = {'m': 0.001}
        try:
            if isinstance(value, (int, float)):  # This only passes if the value is already numericß
                return value

            # prefix conversion
            if value[-1] in prefixes:
                multiplier = prefixes[value[-1]]
                answer = multiplier * float(value[:-1])
            else:
                answer = float(value)
            if self.ampMin <= answer <= self.ampMax:
                return answer
            self.ThrowError("Amplitude must be between {0}V and {1}V.".format(self.ampMin, self.ampMax))
            
        except Exception as e:
            print(e)
            self.ThrowError("Invalid input(s). With value: " + value)
            return 0
    
    # Checks if the user inputted an amplitude value with a prefix and converts it accordingly, also checks for legal values.
    def freq_verification(self, value):
        prefixes = {'K': 1000, 'k': 1000, 'M': 1000000, 'm': 1000000}
        try:
            if isinstance(value, (int, float)): #This only passes if the value has not been changed
                return value
            
            # prefix conversion
            if(len(value) == 1):
                return int(value)
            elif value[-1] in prefixes:
                multiplier = prefixes[value[-1]]
                answer = multiplier * int(value[:-1])
            else:
                answer = int(value)
            
            #Check if values are permitted
            if answer >= self.freqMin and answer <= self.freqMax:
                return int(answer)
            self.ThrowError("Frequency must be between {0}Hz and {1}MHz.".format(self.freqMin, int(self.freqMax/1000000)))
            return 0
        except Exception as e:
            print(e)
            self.ThrowError("Invalid input(s). With value:" + value)
            return 0
    
    #Saves the waveform drawn by the user.
    def save_waveform(self):
        #file_dialog = QtGui.QFileDialog()
        #file_dialog.setDefaultprefix('txt')
        #file_dialog.setNameFilter('Text files (*.txt)')
        #if file_dialog.exec_():
            #file_path = file_dialog.selectedFiles()[0]
            #t, y = self.plot_data.getData()
            #np.savetxt(file_path, y)
        dummy = True

    # Resets the waveform to default settings as the first opened by the user.
    def reset_waveform(self):
        self.freq_slider.setValue(10)
        self.amp_slider.setValue(1)
        self.phase_slider.setValue(0)
        self.sine_button.setChecked(True)
        self.arb_file_label.setText('No file selected')
        self.arbitrary_waveform = None
        self.plot_data.clear()
        i = 0

    def ThrowError(self, message):
        self.errorBox.setText(message)
        self.errorBox.exec()
        
    def closeEvent(self, event):
        self.conn.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    waveform_generator = WaveformGenerator()
    waveform_generator.show()
    
    drawer_window = wave_drawer.AppWindow()
    app.exec()
    #sys.exit(app.exec())

    sys.exit()
    #os._exit (1)