import subprocess
import math
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QComboBox
)
from PyQt6 import QtGui
from wavegen import generateSamples
from connection import Connection
from input_feild import Input

#<<<<<<< HEAD
class WaveSettings():
    def __init__(self, type, freq, amp, offset =0 , duty = 50, phase = 0, arb = None):
        self.type = type
        self.freq = freq
        self.amp = amp
        self.offset = offset
        self.duty = duty
        self.phase = phase
        self.arb = arb

class Channal:
    def update_dropdown(self):
        self.waveform_type = self.dropdown.currentText().lower()

        if (self.waveform_type == 'square'):
            self.freqInput.setEnabled(True)
            self.ampInput.setEnabled(True)
            self.offsetInput.setEnabled(True)
            self.dutyInput.setEnabled(True)
            self.phaseInput.setEnabled(True)
        elif (self.waveform_type == 'dc'):
            self.freqInput.setEnabled(False)
            self.ampInput.setEnabled(False)
            self.offsetInput.setEnabled(True)
            self.dutyInput.setEnabled(False)
            self.phaseInput.setEnabled(False)
        elif (self.waveform_type == 'arbitrary'):
            #dont do this here
            #self.arbitrary_waveform = self.listAW[self.dropdownArb.currentIndex()].samples
            pass
        else:
            self.freqInput.setEnabled(True)
            self.ampInput.setEnabled(True)
            self.offsetInput.setEnabled(True)
            self.dutyInput.setEnabled(False)
            self.phaseInput.setEnabled(True)
        self.generate_waveform()

    def update_dropdownArb(self):
        if self.waveform_type == 'arbitrary':
            self.arbitrary_waveform = self.listAW[self.dropdownArb.currentIndex()].samples
            self.generate_waveform()


    def setRunningStatus(self, status):
        self.running = status
        if self.running:
            self.run_stop.setText("Stop")
            self.run_stop.setIcon(self.stop_icon)
            #self.run_stop.setStyleSheet("background-color : lightblue")
        else:
            self.run_stop.setText("Run")
            self.run_stop.setIcon(self.run_icon)
            #self.run_stop.setStyleSheet("background-color : lightgrey")
        self.generate_waveform()
        
    def generate_waveform(self):
        if not self.initDone:
            return
            
        #Different waveform generations based on waveform type
        tr = 1 / self.freqInput.value
        #arb_wave = self.listAW[self.dropdownArb.currentIndex()].samples
        arb_wave = None
        samples = generateSamples(self.waveform_type, 1000, self.ampInput.value, self.arbitrary_waveform, self.dutyInput.value, self.phaseInput.value / 360, offset = self.offsetInput.value, timeRange = tr, clamp = [-10, 10])
        #if samples[0]:
        #    pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')
             
        self.plot_data.setData(samples[1], samples[2])
        self.plot_widget.setLabel('left', text='', units='V')
        self.plot_widget.setLabel('bottom', text='', units= 's')
        self.plot_widget.setXRange(0, tr)
        
        self.guide_lines[0].setData([-tr, tr * 2], [self.offsetInput.value, self.offsetInput.value])
        self.guide_lines[1].setData([-tr, tr * 2], [self.offsetInput.value + self.ampInput.value, self.offsetInput.value + self.ampInput.value])
        self.guide_lines[2].setData([-tr, tr * 2], [self.offsetInput.value - self.ampInput.value, self.offsetInput.value - self.ampInput.value])
        self.guide_lines[1].setVisible(self.waveform_type != "dc")
        self.guide_lines[2].setVisible(self.waveform_type != "dc")
        
        if self.running:
            self.waveSettings = WaveSettings(type = self.waveform_type, freq = self.freqInput.value, amp = self.ampInput.value, offset = self.offsetInput.value, duty = self.dutyInput.value, phase = self.phaseInput.value / 360, arb = self.arbitrary_waveform)
            #self.conn.sendWave(self.chan_num, freq = self.freqInput.value, wave_type = self.waveform_type, amplitude = self.ampInput.value, offset = self.offsetInput.value, arbitrary_waveform = None, duty = self.dutyInput.value, phase = self.phaseInput.value / 360)
        else:
            self.waveSettings = WaveSettings(type = "dc", freq = 1e3, amp = 5)
            #self.conn.sendWave(self.chan_num, wave_type = "dc", offset = 0)
        
        if self.allowUpdates:
            self.updateWave(self.chan_num)
        
        if self.running:
            self.on_off_label.setText("ON")
            self.on_off_label.setColor((0, 255, 0))
        else:
            self.on_off_label.setText("OFF")
            self.on_off_label.setColor((255, 0, 0))


    def enableUpdates(self):
        self.allowUpdates = True
        self.updateWave(self.chan_num)
        
    def updateAWList(self, AWlist):
        self.listAW = AWlist
        self.dropdownArb.clear()
        for aw in self.listAW:
            self.dropdownArb.addItem(aw.filename)

    def __init__(self, chan_num, grid_layout, run_icon, stop_icon, updateWave):
        self.run_icon = run_icon
        self.stop_icon = stop_icon
        self.chan_num = chan_num
        self.updateWave = updateWave
        
        if chan_num == 0:
            GUI_OFFSET = 0
        elif chan_num == 1:
            GUI_OFFSET = 9
            
        self.initDone = False
        self.allowUpdates = False
        self.arbitrary_waveform = None
        self.waveform_type = "sine"
        self.listAW = []

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setLabel('left', text='', units='V')
        self.plot_widget.setLabel('bottom', text='', units='s')
        self.plot_widget.setYRange(-10, 10)
        self.plot_widget.hideButtons()

        self.guide_lines = []
        for i in range(3):
            if chan_num == 0:
                self.guide_lines.append(self.plot_widget.plot(pen=(255, 255, 0, 96)))
                # self.guide_lines.append(self.plot_widget.plot(pen=pg.mkPen(color='y', dash=[5, 5])))
            elif chan_num == 1:
                self.guide_lines.append(self.plot_widget.plot(pen=(0, 255, 255, 96)))
                # self.guide_lines.append(self.plot_widget2.plot(pen=pg.mkPen(color='c', dash=[5, 5])))

        COLORS = ['y', 'c']
        self.plot_data = self.plot_widget.plot(pen=COLORS[chan_num])

        self.on_off_label = pg.TextItem()
        self.on_off_label.setPos(0, 10)
        self.plot_widget.addItem(self.on_off_label)

        self.clabel = QtWidgets.QLabel(f'Channel {chan_num + 1}')

        prefixes_v = {"m": 1e-3}
        prefixes_f = {"K": 1e3, "M": 1e6}

        self.freq_label = QtWidgets.QLabel('Frequency (Hz):')
        self.freqInput = Input(self.generate_waveform, [1, 250e3], float(1000), "hz", prefixes_f)

        self.amp_label = QtWidgets.QLabel('Amplitude:')
        self.ampInput = Input(self.generate_waveform, [-5, 5], float(5), "v", prefixes_v)

        self.offset_label = QtWidgets.QLabel('Offset voltage:')
        self.offsetInput = Input(self.generate_waveform, [-10, 10], float(0), "v", prefixes_v)

        self.DCLabel = QtWidgets.QLabel("Duty Cycle:")
        self.dutyInput = Input(self.generate_waveform, [0, 100], float(50), "%", [])
        
        self.phaseLabel = QtWidgets.QLabel("Phase (Deg):")
        self.phaseInput = Input(self.generate_waveform, [0, 360], float(0), "deg", [])

        self.run_stop = QtWidgets.QPushButton()
        self.run_stop.clicked.connect(lambda: self.setRunningStatus(not self.running))
        
        self.wavetypeLabel = QtWidgets.QLabel("Wave type")
        self.dropdown = QComboBox()
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')
        self.dropdown.addItem('Arbitrary')
        self.dropdown.addItem('DC')
        self.dropdown.activated.connect(self.update_dropdown)

        self.arbwaveLabel = QtWidgets.QLabel("Arbitrary Wave:")
        self.dropdownArb = QComboBox()
        for aw in self.listAW:
            self.dropdownArb.addItem(aw.filename)
        self.dropdownArb.activated.connect(self.update_dropdownArb)

        grid_layout.addWidget(self.plot_widget, GUI_OFFSET + 1, 0, 9, 5)
        grid_layout.addWidget(self.clabel, GUI_OFFSET + 1, 5, 1, 1)

        grid_layout.addWidget(self.freq_label, GUI_OFFSET + 2, 5, 1, 1)
        grid_layout.addWidget(self.freqInput, GUI_OFFSET + 2, 6, 1, 1)

        grid_layout.addWidget(self.amp_label, GUI_OFFSET + 3, 5, 1, 1)
        grid_layout.addWidget(self.ampInput, GUI_OFFSET + 3, 6, 1, 1)

        grid_layout.addWidget(self.offset_label, GUI_OFFSET + 4, 5, 1, 1)
        grid_layout.addWidget(self.offsetInput, GUI_OFFSET + 4, 6, 1, 1)

        grid_layout.addWidget(self.wavetypeLabel, GUI_OFFSET + 7, 5, 1, 1)
        grid_layout.addWidget(self.dropdown, GUI_OFFSET + 7, 6, 1, 1)
        grid_layout.addWidget(self.arbwaveLabel, GUI_OFFSET + 8, 5, 1, 1)
        grid_layout.addWidget(self.dropdownArb, GUI_OFFSET + 8, 6, 1, 1)

        grid_layout.addWidget(self.DCLabel, GUI_OFFSET + 5, 5, 1, 1)
        grid_layout.addWidget(self.dutyInput, GUI_OFFSET + 5, 6, 1, 1)
        grid_layout.addWidget(self.phaseLabel, GUI_OFFSET + 6, 5, 1, 1)
        grid_layout.addWidget(self.phaseInput, GUI_OFFSET + 6, 6, 1, 1)

        grid_layout.addWidget(self.run_stop, GUI_OFFSET + 9, 5, 1, 2)

        self.update_dropdown()
        self.setRunningStatus(False)
        self.initDone = True
        self.generate_waveform()