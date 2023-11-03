import subprocess
import math
import numpy as np
import pyqtgraph as pg
from connection import Connection
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,QComboBox
)
from PyQt6 import QtGui
from wavegen import generateSamples
from aw import AW

class Channal:
    def update_dropdown(self):
        self.waveform_type = self.dropdown.currentText().lower()
        if (self.waveform_type == 'square'):
            self.DCSelect.setEnabled(True)
        elif(self.waveform_type == 'dc'):
            self.freqSelect.setEnabled(False)
            self.ampSelect.setEnabled(False)
        elif(self.waveform_type == 'arbitrary'):
            self.dropdownArb.setEnabled(True)
            self.DCSelect.setEnabled(False)
            self.freqSelect.setEnabled(True)
            self.ampSelect.setEnabled(True)
        else:
            self.DCSelect.setEnabled(False)
            self.freqSelect.setEnabled(True)
            self.ampSelect.setEnabled(True)
        self.generate_waveform()

    def updateArb_Dropdown(self):
        self.arbitrary_waveform = self.dropdownArb.currentText().lower()
        self.listAW = []
        self.dropdownArb.clear()
        f = open("saved.txt", "r")
        for line in f:
            self.dropdownArb.addItem(line[0: line.find(',')])
            strArray = line[line.find('[') + 1: len(line) - 2]
            strArray = strArray.split(", ")
            arr = [float(val) for val in strArray]
            self.listAW.append(AW(line[0: line.find(',')], arr))
        self.dropdownArb.activated.connect(lambda: self.updateArb_Dropdown())
        self.generate_waveform()

    def toggleRunningStatus(self):
        self.running = not self.running
        if self.running:
            self.run_stop.setText("Stop")
            self.run_stop.setIcon(self.stop_icon)
        else:
            self.run_stop.setText("Run")
            self.run_stop.setIcon(self.run_icon)
        self.generate_waveform()
        
    def generate_waveform(self):
        #Different waveform generations based on waveform type
        tr = 1 / self.freq
        samples = generateSamples(self.waveform_type, 1000, self.amplitude, self.arbitrary_waveform, self.dutyCycle, self.phase, offset = self.offset, timeRange = tr)
        if samples[0]:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')
             
        self.plot_data.setData(samples[1], samples[2])
        self.plot_widget.setLabel('left', text='', units='V')
        self.plot_widget.setLabel('bottom', text='', units= 's')
        self.plot_widget.setXRange(0, tr)
        
        self.guide_lines[0].setData([-tr, tr * 2], [self.offset, self.offset])
        self.guide_lines[1].setData([-tr, tr * 2], [self.offset + self.amplitude, self.offset + self.amplitude])
        self.guide_lines[2].setData([-tr, tr * 2], [self.offset - self.amplitude, self.offset - self.amplitude])
        self.guide_lines[1].setVisible(self.waveform_type != "dc")
        self.guide_lines[2].setVisible(self.waveform_type != "dc")
        #self.conn.sendWave(0, self.freq, self.waveform_type, self.amplitude, self.offset, self.arbitrary_waveform)
     
        if self.running:
            self.on_off_label.setText("ON")
            #self.on_off_label.setAttr("color", "#00FF00")
            self.on_off_label.setColor((0, 255, 0))
        else:
            self.on_off_label.setText("OFF")
            ##self.on_off_label.setAttr(color = (255, 0, 0))
            self.on_off_label.setColor((255, 0, 0))
            
    prefixes_v = {"m" : 1e-3}
    prefixes_f = {"K" : 1e3, "M" : 1e6}
    
    def findBestPrefix(self, val, prefixes):
        for p in prefixes:
            n_val = val / prefixes[p]
            if n_val >= 1 and n_val < 1e3:
                return (n_val, p)
        return (val, "")
                
    def endsWithLower(self, str, str2):
        return str[-len(str2):].lower() == str2.lower()
            
    def parseStringToVal(self, str_in, prefixes, expected_unit):
        str_in = str_in.replace(" ", "")
        
        if self.endsWithLower(str_in, expected_unit):
            str_in = str_in[:-len(expected_unit)]
            
        mag = 1
        if prefixes:
            for p in prefixes:
                if self.endsWithLower(str_in, p):
                    str_in = str_in[:-len(p)]
                    mag = prefixes[p]
        
        try:
            val = float(str_in)
        except Exception as e:
            return None
            
        return val * mag
    
    def fixRange(self, val, minVal, maxVal):
        return min(maxVal, max(minVal, val))
            
    def setFreq(self, val):
        self.freq = val
        val, prefix = self.findBestPrefix(val, self.prefixes_f)
        self.freqSelect.setText(f"{val} {prefix}hz")
        if self.initDone:
            self.generate_waveform()
        
    def setAmp(self, val):
        self.amplitude = val
        val, prefix = self.findBestPrefix(val, self.prefixes_v)
        self.ampSelect.setText(f"{val} {prefix}V")
        if self.initDone:
            self.generate_waveform()
        
    def setOffset(self, val):
        self.offset = val
        val, prefix = self.findBestPrefix(val, self.prefixes_v)
        self.offsetSelect.setText(f"{val} {prefix}V")
        if self.initDone:
            self.generate_waveform()
        
    def setDC(self, val):
        self.dutyCycle = val
        #val, prefix = self.findBestPrefix(val, None)
        self.DCSelect.setText(f"{val} %")
        if self.initDone:
            self.generate_waveform()
        
    def setPhase(self, val):
        self.phase = val
        #val, prefix = self.findBestPrefix(val, None)
        self.phaseSelect.setText(f"{val} deg")
        if self.initDone:
            self.generate_waveform()

    def updateFreq(self):
        val = self.parseStringToVal(self.freqSelect.text(), self.prefixes_f, "hz")
        if val is None:
            self.freqSelect.undo()
        else:
            val = self.fixRange(abs(val), 0, 250e3)
            self.setFreq(val)
        
    def updateAmp(self):
        val = self.parseStringToVal(self.ampSelect.text(), self.prefixes_v, "V")
        if val is None:
            self.ampSelect.undo()
        else:
            val = self.fixRange(val, -5, 5)
            self.setAmp(val)
        
    def updateOffset(self):
        val = self.parseStringToVal(self.offsetSelect.text(), self.prefixes_v, "V")
        if val is None:
            self.offsetSelect.undo()
        else:
            range = 5 if self.waveform_type != "dc" else 10
            val = self.fixRange(val, -range, range)
            self.setOffset(val)
        
    def updateDC(self):
        val = self.parseStringToVal(self.DCSelect.text(), None, "%")
        if val is None:
            self.DCSelect.undo()
        else:
            val = self.fixRange(abs(val), 0, 100)
            self.setDC(val)
        
    def updatePhase(self):
        val = self.parseStringToVal(self.phaseSelect.text(), None, "deg")
        if val is None:
            self.phaseSelect.undo()
        else:
            val = self.fixRange(abs(val), 0, 360)
            self.setPhase(val)

    def __init__(self, chan_num, grid_layout, run_icon, stop_icon, conn):
        self.run_icon = run_icon
        self.stop_icon = stop_icon
    
        if chan_num == 0:
            GUI_OFFSET = 0
        elif chan_num == 1:
            GUI_OFFSET = 8
   
        self.running = True #this will be toggled to False before we leave init()
        
        self.initDone = False
        self.freq = -1
        self.amplitude = -1
        self.offset = -1
        self.dutyCycle = -1
        self.phase = -1
        self.arbitrary_waveform = None
        self.waveform_type = "sine"
        
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
                #self.guide_lines.append(self.plot_widget.plot(pen=pg.mkPen(color='y', dash=[5, 5])))
            elif chan_num == 1:
                self.guide_lines.append(self.plot_widget.plot(pen=(0, 255, 255, 96)))
                #self.guide_lines.append(self.plot_widget2.plot(pen=pg.mkPen(color='c', dash=[5, 5])))
        
        COLORS = ['y', 'c']
        self.plot_data = self.plot_widget.plot(pen=COLORS[chan_num])
                   
        self.on_off_label = pg.TextItem()      
        self.on_off_label.setPos(0, 10)   
        self.plot_widget.addItem(self.on_off_label)
           
           
        self.clabel = QtWidgets.QLabel(f'Channel {chan_num + 1}')

        self.freq_label = QtWidgets.QLabel('Frequency (Hz):')
        self.freqSelect = QLineEdit()
        self.setFreq(float(1000))
        self.freqSelect.editingFinished.connect(self.updateFreq)
    
        self.amp_label = QtWidgets.QLabel('Amplitude:')
        self.ampSelect = QLineEdit()
        self.setAmp(float(5))
        self.ampSelect.editingFinished.connect(self.updateAmp)

        self.offset_label = QtWidgets.QLabel('Offset voltage:')
        self.offsetSelect = QLineEdit()
        self.setOffset(float(0))
        self.offsetSelect.editingFinished.connect(self.updateOffset)

        self.DCLabel = QtWidgets.QLabel("Duty Cycle:")
        self.DCSelect = QLineEdit()
        self.DCSelect.setEnabled(False)
        self.setDC(float(50))
        self.DCSelect.editingFinished.connect(self.updateDC)
        
        self.phaseLabel = QtWidgets.QLabel("Phase (Deg):")
        self.phaseSelect = QLineEdit()
        self.setPhase(float(0))
        self.phaseSelect.editingFinished.connect(self.updatePhase)
        #self.phaseSelect.setEnabled(False)
       
        self.arb_file_label = QtWidgets.QLabel('No file selected')
        self.arb_file_button = QtWidgets.QPushButton('Select file')
        self.arb_file_button.setEnabled(False)
        self.run_stop = QtWidgets.QPushButton()
        self.run_stop.clicked.connect(self.toggleRunningStatus)

        self.listAW = []
        self.dropdownArb = QComboBox()
        f = open("saved.txt", "r")
        for line in f:
            self.dropdownArb.addItem(line[0: line.find(',')])
            strArray = line[line.find('[') + 1: len(line) - 2]
            strArray = strArray.split(", ")
            arr = [float(val) for val in strArray]
            self.listAW.append(AW(line[0: line.find(',')], arr))
        self.dropdownArb.activated.connect(lambda: self.updateArb_Dropdown())
        #self.dropdownArb.setEnabled(False)

        self.dropdown = QComboBox()
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')
        self.dropdown.addItem('Arbitrary')
        self.dropdown.addItem('DC')
        self.dropdown.activated.connect(lambda: self.update_dropdown())
        
        grid_layout.addWidget(self.plot_widget, GUI_OFFSET + 1, 0, 8, 5)
        grid_layout.addWidget(self.clabel, GUI_OFFSET + 1, 5, 1, 1)
        
        grid_layout.addWidget(self.freq_label, GUI_OFFSET + 2, 5, 1, 1)
        grid_layout.addWidget(self.freqSelect, GUI_OFFSET + 2, 6, 1, 1)
        
        grid_layout.addWidget(self.amp_label, GUI_OFFSET + 3, 5, 1, 1)
        grid_layout.addWidget(self.ampSelect, GUI_OFFSET + 3, 6, 1, 1)
        
        grid_layout.addWidget(self.offset_label, GUI_OFFSET + 4, 5, 1, 1)
        grid_layout.addWidget(self.offsetSelect, GUI_OFFSET + 4, 6, 1, 1)
        
        grid_layout.addWidget(self.dropdown, GUI_OFFSET + 7, 5, 1, 1)
        grid_layout.addWidget(self.DCLabel, GUI_OFFSET + 5, 5, 1, 1)
        grid_layout.addWidget(self.DCSelect, GUI_OFFSET + 5, 6, 1, 1)
        grid_layout.addWidget(self.phaseLabel, GUI_OFFSET + 6, 5, 1, 1)
        grid_layout.addWidget(self.phaseSelect, GUI_OFFSET + 6, 6, 1, 1)
        
        grid_layout.addWidget(self.dropdownArb, GUI_OFFSET + 7, 6, 1, 1)
        grid_layout.addWidget(self.run_stop, GUI_OFFSET + 8, 5, 1, 2)
        
        self.toggleRunningStatus()
        self.initDone = True
        self.generate_waveform()
