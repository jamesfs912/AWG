import importlib
import subprocess
import sys 
import os
import wave_drawer
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
from PyQt6.QtCore import Qt
from PyQt6 import QtGui
from wavegen import generateSamples
import threading
import platform
from channel import Channel

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
                c.setRunningStatus(False)

    def connectButtonClicked(self):
        self.connectButton.setEnabled(False)
        self.conn.tryConnect()
       
    def setSyncStatus(self, status):
        if status:
            self.synced_status.setText("Synced")
            self.synced_status.setStyleSheet("color : green")
        else:
            self.synced_status.setText("Not Synced")
            self.synced_status.setStyleSheet("color : red")
    
    def updateWave(self, changed = -1):
        set = [self.channels[0].waveSettings, self.channels[1].waveSettings]
        syncNotPossible = (set[0].type == "dc" or set[1].type == "dc")
        if not(self.syncButton.isChecked()) or syncNotPossible:
            if changed == 0 or changed == -1:
                self.conn.sendWave(0, freq = set[0].freq, wave_type = set[0].type, amplitude = set[0].amp, offset = set[0].offset, arbitrary_waveform = None, duty = set[0].duty, phase = set[0].phase)
            if changed == 1 or changed == -1:
                self.conn.sendWave(1, freq = set[1].freq, wave_type = set[1].type, amplitude = set[1].amp, offset = set[1].offset, arbitrary_waveform = None, duty = set[1].duty, phase = set[1].phase)
            if syncNotPossible:
                self.setSyncStatus(False)
            else:
                ns0, arr0, psc0 = self.conn.calc_val(set[0].freq)
                ns1, arr1, psc1 = self.conn.calc_val(set[1].freq)
                synced = (ns1 * (arr1 + 1) * (psc1 + 1)) / (ns0 * (arr0 + 1) * (psc0 + 1)) == (set[0].freq / set[1].freq)
                self.setSyncStatus(synced)
        else:
            min = None
            for a in range(1, 101):
                for b in range(1, 101):
                    if a/b == set[0].freq / set[1].freq:
                        if min == None or min[0] * min[1] > a*b:
                            min = (a, b)
            if min == None:
                self.conn.sendWave(0, freq = set[0].freq, wave_type = set[0].type, amplitude = set[0].amp, offset = set[0].offset, arbitrary_waveform = None, duty = set[0].duty, phase = set[0].phase)
                self.conn.sendWave(1, freq = set[1].freq, wave_type = set[1].type, amplitude = set[1].amp, offset = set[1].offset, arbitrary_waveform = None, duty = set[1].duty, phase = set[1].phase)
                self.setSyncStatus(False)
            else:
                a, b = min
                f_comm = set[0].freq / a #same as set[1].freq / b
                self.conn.sendWave(0, f_comm, wave_type = set[0].type, amplitude = set[0].amp, offset = set[0].offset, arbitrary_waveform = None, duty = set[0].duty, phase = set[0].phase, numPeriods = a)
                self.conn.sendWave(1, f_comm, wave_type = set[1].type, amplitude = set[1].amp, offset = set[1].offset, arbitrary_waveform = None, duty = set[1].duty, phase = set[1].phase, numPeriods = b)
                self.setSyncStatus(True)
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Waveform Generator')
        
        self.grid_layout = QtWidgets.QGridLayout()
        
        self.setWindowIcon(QtGui.QIcon(resource_path("icon/icon.ico")))
        icons = {}
        for x in ["run", "stop", "sine", "tri", "saw", "square", "arb", "dc"]:
            icons[x] = QtGui.QIcon(resource_path("icon/" + x + ".png"))
        
        self.grid_layout.addWidget(QtWidgets.QLabel("Waveform generator"), 0, 0, 1, 1)
        
        self.synced_status = QtWidgets.QLabel("")
        self.grid_layout.addWidget(self.synced_status, 0, 5, 1, 1)
        #self.synced_status.setPixmap(stop_icon.pixmap())
        self.setSyncStatus(False)
        
        self.syncButton = QtWidgets.QCheckBox  ("Force Sync")
        self.grid_layout.addWidget(self.syncButton, 0, 6, 1, 1)
        self.syncButton.clicked.connect(lambda: self.updateWave(-1))
        
        self.open_drawer = QtWidgets.QPushButton('Open Wave Drawer')
        self.grid_layout.addWidget(self.open_drawer, 0, 1)
        self.open_drawer.clicked.connect(self.fun_open_drawer)
 
        self.statusCallbackSignal.connect(self.statusCallback)
        self.conn = Connection(self.statusCallbackSignal)
 
        self.channels = []
        for i in range(2):
            self.channels += [Channel(i, self.grid_layout, icons, self.updateWave)]
        for c in self.channels:
            c.enableUpdates()
            
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
        self.themeList = {'Default' : self.defaultTheme, 'Blue Mode' : self.lightMode, 'Dark Mode' : self.darkMode}
        self.themeDropdown.addItems(self.themeList.keys())
        self.themeDropdown.currentTextChanged.connect(lambda: self.themeList[self.themeDropdown.currentText()]())

        # Custom width dropdown menu
        self.themeDropdown.view().setFixedWidth(125)
        themeLayout.addWidget(self.themeDropdown)
        self.grid_layout.addLayout(themeLayout, 19, 2, 1, 1)

        for i in range(1, 7):
            self.grid_layout.setColumnStretch(i, 1)
        for i in range(0, 19):
            self.grid_layout.setRowStretch(i, 1)
      
        self.setLayout(self.grid_layout)

        self.defaultTheme()

    def fun_open_drawer(self):
        drawer_window.show()
        
    def closeEvent(self, event):
        self.conn.close()

    def defaultTheme(self):
        if platform.system() != "Darwin":
            app.setStyleSheet("")
        else:
            app.setStyle("fusion")
            app.setStyleSheet("""
                QWidget {
                    font-family: 'Verdana', sans-serif;
                    font-size: 12px;
                    color: #000000;
                    background-color: #ffffff;  
                }
            
                QLineEdit, QComboBox, QTextEdit {
                    border: 1px solid #000; 
                    padding: 2px;
                    background-color: #FFFFFF;
                    color: #000000;
                }
            
                QPushButton {
                    font-family: 'Verdana', sans-serif;
                    color: #000000;
                    background-color: #E0E0E0;  
                    border: 1px solid #000; 
                    padding: 5px 10px;
                }""")

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

    drawer_window = wave_drawer.AppWindow(waveform_generator.channels)
    app.exec()
    sys.exit()