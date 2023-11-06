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

import subprocess
import math
import numpy as np
import pyqtgraph as pg
from connection import Connection
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QToolBar, QPushButton, QVBoxLayout, QFrame, QLabel, QMessageBox,QComboBox
)
from PyQt6 import QtGui
from wavegen import generateSamples
import threading
import platform
from channal import Channal

#why windows why?
if platform.system() == "Windows":
    import ctypes
    myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
        
class WaveformGenerator(QtWidgets.QWidget):
    statusCallbackSignal = pyqtSignal(str, str)

    def statusCallback(self, status, message):
        self.status_label.setText("Status: " + status)
        self.connectButton.setEnabled(status == "disconnected")
        if message:
            pg.QtWidgets.QMessageBox.critical(self, 'Error', message)
        if status == "connected":
            for c in self.channels:
                print(c.chan_num)
                #c.setRunningStatus(False)

    def connectButtonClicked(self):
        self.connectButton.setEnabled(False)
        self.conn.tryConnect()
    
    def synButtonClicked(self):
        pass
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waveform Generator')
        
        self.grid_layout = QtWidgets.QGridLayout()
        
        self.setWindowIcon(QtGui.QIcon(resource_path("icon/icon.ico")))
        run_icon = QtGui.QIcon(resource_path("icon/run.png"))
        stop_icon = QtGui.QIcon(resource_path("icon/stop.png"))
        
        self.grid_layout.addWidget(QtWidgets.QLabel("Waveform generator"), 0, 0, 1, 1)
        self.syncButton = QtWidgets.QPushButton("Sync")
        self.grid_layout.addWidget(self.syncButton, 0, 6, 1, 1)
        self.syncButton.clicked.connect(self.synButtonClicked)

        self.open_drawer = QtWidgets.QPushButton('open sock drawer')
        self.grid_layout.addWidget(self.open_drawer, 0, 5)
        self.open_drawer.clicked.connect(self.fun_open_drawer)
 
        self.statusCallbackSignal.connect(self.statusCallback)
        self.conn = Connection(self.statusCallbackSignal)
 
        self.channels = []
        for i in range(2):
            self.channels += [Channal(i, self.grid_layout, run_icon, stop_icon, self.conn)]

        self.status_label = QtWidgets.QLabel("Status: disconnected")
        self.grid_layout.addWidget(self.status_label, 19, 0, 1, 1)
        
        self.connectButton = QtWidgets.QPushButton("Connect")
        self.connectButton.setEnabled(False)
        self.grid_layout.addWidget(self.connectButton, 19, 1, 1, 1)
        self.connectButton.clicked.connect(self.connectButtonClicked)

        # Theme H Layout
        themeLayout = QtWidgets.QHBoxLayout()

        # Dropdown label
        themeLabel = QtWidgets.QLabel("Theme:")
        themeLayout.addWidget(themeLabel)

        # Theme Dropdown
        self.themeDropdown = QtWidgets.QComboBox()
        self.themeDropdown.addItems(['Default', 'Light Mode', 'Dark Mode'])
        self.themeDropdown.currentTextChanged.connect(self.onThemeChange)

        # Custom width dropdown menu
        self.themeDropdown.view().setFixedWidth(100)
        themeLayout.addWidget(self.themeDropdown)


        self.grid_layout.addLayout(themeLayout, 19, 2, 1, 1)

        # # Theme Dropdown
        # self.themeDropdown = QComboBox()
        # self.themeDropdown.addItem('Light Mode')
        # self.themeDropdown.addItem('Dark Mode')
        # self.themeDropdown.currentTextChanged.connect(self.onThemeChange)

        # # Theme Dropdown grid
        # self.grid_layout.addWidget(self.themeDropdown, 19, 2, 1, 1)

        for i in range(1, 6):
            self.grid_layout.setColumnStretch(i, 1)
        
        for i in range(0, 16):
            self.grid_layout.setRowStretch(i, 1)
      
        self.setLayout(self.grid_layout)

        self.defaultTheme()

#    def init_restraints(self):
#        #Hardware restraints
#        self.freqMin = 0
#        self.freqMax = 1000000
#        self.ampMin = 0
#        self.ampMax = 5
#        self.offsetMin = -5
#        self.offsetMax = 5

    def fun_open_drawer(self):
        drawer_window.show()
    
#    # Takes the user inputted CSV files and loads them as the current waveform
#    def select_arbitrary_file(self):
#        file_dialog = QtWidgets.QFileDialog()
#        file_dialog.setNameFilter('csv files (*.csv)')
#        if file_dialog.exec():
#            file_path = file_dialog.selectedFiles()[0]
#            self.arb_file_label.setText(file_path)
#            self.arbitrary_waveform = np.loadtxt(file_path)
#
#    # Takes the user inputted CSV files and loads them as the current waveform
#    def select_c2_arbitrary_file(self):
#        file_dialog = QtWidgets.QFileDialog()
#        file_dialog.setNameFilter('csv files (*.csv)')
#        if file_dialog.exec():
#            file_path = file_dialog.selectedFiles()[0]
#            self.c2_arb_file_label.setText(file_path)
#            self.c2_arbitrary_waveform = np.loadtxt(file_path)
#
#    # Generates the waveform from the 
#    def load_arbitrary_waveform(self):
#        try:
#            # Read the CSV file and update the waveform data
#            self.arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
#            self.generate_waveform()
#        except OSError:
#            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')
#
#    # Generates the waveform from the file saved by the user. Note to Vik: You might have to change the filename to not conflict with c1 and c2
#    def load_c2_arbitrary_waveform(self):
#        try:
#            # Read the CSV file and update the waveform data
#            self.c2_arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
#            self.generate_waveform()
#        except OSError:
#            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')
#
#    def phase_verification(self, value):
#        try:
#            value = int(value)
#            value = value % 360
#            return value
#        except:
#            self.ThrowError("Invalid input, phase can only be an integer value.")
#            return 0    
#
#    def duty_verification(self, value):
#        try:
#            value = int(value)
#            if value >= 0 and value <= 100:
#                return value
#            self.ThrowError("Duty cycle must be between 0 and 100.")
#            return 0
#        except:
#            self.ThrowError("Invalid input, duty cycle can only be an integer value.")
#            return 0
#
#    def offset_verification(self, value, channel = 0):
#        prefixes = {'m': 0.001, 'V': 1, 'v': 1, 'mV': 0.001, 'mv': 0.001}
#        try:
#            if isinstance(value, (int, float)):  # This only passes if the value is already numeric
#                return value
#            print("Offset: " + value)
#            # prefix conversion
#            if value[-2:] in prefixes:
#                multiplier = prefixes[value[-2:]]
#                answer = multiplier * float(value[:-2])
#            elif value[-1] in prefixes:
#                multiplier = prefixes[value[-1]]
#                answer = multiplier * float(value[:-1])
#            else:
#                answer = float(value)
#            
#            if(channel == 1):
#                if(self.waveform_type == 'dc'):
#                    if(-10 <= answer <= 10):
#                        return answer
#                    else:
#                        self.ThrowError("Voltage must be between -10V and 10V.")
#                        return 0
#                elif(self.offsetMin <= answer <= self.offsetMax):
#                    return answer
#                else:
#                    
#                    self.ThrowError("Voltage must be between {0}V and {1}V.".format(self.offsetMin, self.offsetMax))
#                    return 0
#            if(channel == 2):
#                if(self.c2_waveform_type == 'dc'):
#                    if(-10 <= answer <= 10):
#                        return answer
#                    else:
#                        self.ThrowError("Voltage must be between -10V and 10V.")
#                        return 0
#                elif(self.c2_offsetMin <= answer <= self.c2_offsetMax):
#                    return answer
#                else:
#                    self.ThrowError("Voltage must be between {0}V and {1}V.".format(self.offsetMin, self.offsetMax))
#                    return 0
#
#            self.ThrowError("Voltage must be between {0}V and {1}V.".format(self.offsetMin, self.offsetMax))
#            return 0
#        
#        except Exception as e:
#            print(e)
#            self.ThrowError("Invalid input(s). With value: " + value)
#            return 0
#        
#    def amplitude_verification(self, value):
#        prefixes = {'m': 0.001}
#        try:
#            if isinstance(value, (int, float)):  # This only passes if the value is already numericß
#                return value
#
#            # prefix conversion
#            if value[-1] in prefixes:
#                multiplier = prefixes[value[-1]]
#                answer = multiplier * float(value[:-1])
#            else:
#                answer = float(value)
#            if self.ampMin <= answer <= self.ampMax:
#                return answer
#            self.ThrowError("Amplitude must be between {0}V and {1}V.".format(self.ampMin, self.ampMax))
#            
#        except Exception as e:
#            print(e)
#            self.ThrowError("Invalid input(s). With value: " + value)
#            return 0
#    
#    # Checks if the user inputted an amplitude value with a prefix and converts it accordingly, also checks for legal values.
#    def freq_verification(self, value):
#        prefixes = {'K': 1000, 'k': 1000, 'M': 1000000, 'm': 1000000}
#        try:
#            if isinstance(value, (int, float)): #This only passes if the value has not been changed
#                return value
#            
#            # prefix conversion
#            if(len(value) == 1):
#                return int(value)
#            elif value[-1] in prefixes:
#                multiplier = prefixes[value[-1]]
#                answer = multiplier * int(value[:-1])
#            else:
#                answer = int(value)
#            
#            #Check if values are permitted
#            if answer >= self.freqMin and answer <= self.freqMax:
#                return int(answer)
#            self.ThrowError("Frequency must be between {0}Hz and {1}MHz.".format(self.freqMin, int(self.freqMax/1000000)))
#            return 0
#        except Exception as e:
#            print(e)
#            self.ThrowError("Invalid input(s). With value:" + value)
#            return 0
#    
#    #Saves the waveform drawn by the user.
#    def save_waveform(self):
#        #file_dialog = QtGui.QFileDialog()
#        #file_dialog.setDefaultprefix('txt')
#        #file_dialog.setNameFilter('Text files (*.txt)')
#        #if file_dialog.exec_():
#            #file_path = file_dialog.selectedFiles()[0]
#            #t, y = self.plot_data.getData()
#            #np.savetxt(file_path, y)
#        dummy = True
#
#    # Resets the waveform to default settings as the first opened by the user.
#    def reset_waveform(self):
#        self.freq_slider.setValue(10)
#        self.amp_slider.setValue(1)
#        self.phase_slider.setValue(0)
#        self.sine_button.setChecked(True)
#        self.arb_file_label.setText('No file selected')
#        self.arbitrary_waveform = None
#        self.plot_data.clear()
#        i = 0
        
    def closeEvent(self, event):
        self.conn.close()
        
    def defaultTheme(self):
        app.setStyleSheet("""
            QWidget {
                font-family: 'Verdana', sans-serif;
                font-size: 12px;
                color: #000000;
                background-color: #ffffff;  /* Set a neutral background color */
            }

            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #000; /* Use a standard border */
                padding: 2px;
                background-color: #FFFFFF;
                color: #000000;
            }

            QPushButton {
                font-family: 'Verdana', sans-serif;
                color: #000000;
                background-color: #E0E0E0;  /* Neutral background color */
                border: 1px solid #000; /* Standard border */
                padding: 5px 10px;
            }""")

    def onThemeChange(self, text):

        if text == "Light Mode":
            self.lightMode()
        elif text == "Dark Mode":
            self.darkMode()
        elif text == "Default":
            self.defaultTheme()

    def lightMode(self):
        app.setStyleSheet("""
            QWidget {
                font-family: 'Verdana', sans-serif;
                font-size: 12px;
                color: #000000;
                background-color: #0F3E62; 
            }

            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #105C8D; 
                padding: 2px;
                background-color: #FFFFFF;
                color: #000000;
                border-radius: 2px; 
            }

            QPushButton {
                font-family: 'Verdana', sans-serif;
                color: #FFFFFF;
                background-color: #1874CD; 
                border-radius: 5px; 
                padding: 5px 10px;
                border: 1px solid #105C8D; 
            }

            QPushButton:hover {
                background-color: #1C86EE; 
            }

            QPushButton:disabled {
                background-color: #1874CD;
                color: #FFFFFF;
            }

            QLabel {
                color: #FFFFFF; 
            }

    
            QLabel#freqLabel, #ampLabel, #offsetLabel, #dcLabel, #phaseLabel{
                background-color: #1874CD; 
                border: 2px solid #1874CD; 
                border-radius: 5px; 
                padding: 2px; 
                color: white;
            }
            """)
        pass

    def darkMode(self):
        app.setStyleSheet("""
            QWidget {
                font-family: 'Verdana', sans-serif; 
                font-size: 12px;
                color: #E0E0E0; 
                background-color: #2C2C2C; 
            }

            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #3C3C3C; 
                padding: 2px;
                background-color: #2E2E2E; 
                color: #E0E0E0; 
            }

            QPushButton {
                color: #FFFFFF; 
                background-color: #32B58F; 
                border-radius: 4px; 
                padding: 5px 10px;
                border: none; 
            }

            QPushButton:hover {
                background-color: #2D9C8F; 
            }

            QPushButton:disabled {
                background-color: #5E5E5E; 
                color: #3C3C3C;
            }

            QLabel {
                color: #E0E0E0; 
            }

            QCheckBox, QRadioButton {
                color: #E0E0E0; 
            }

            QGroupBox {
                border: 1px solid #3C3C3C; 
                margin-top: 20px; 
            }

            QGroupBox::title {
                color: #E0E0E0; 
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }

            QSlider::groove:horizontal {
                border: 1px solid #3C3C3C; 
                height: 8px;
                background: #2C2C2C;
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                background: #32B58F;
                border: 1px solid #2C2C2C;
                width: 18px;
                margin: -2px 0;
            }

            QSlider::add-page:horizontal {
                background: #555;
            }

            QSlider::sub-page:horizontal {
                background: #32B58F;
            }
            """)
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    waveform_generator = WaveformGenerator()

    waveform_generator.show()
    waveform_generator.connectButtonClicked()

    drawer_window = wave_drawer.AppWindow(waveform_generator.channels[0], waveform_generator.channels[1])
    app.exec()

    sys.exit()
