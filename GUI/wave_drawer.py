import sys

import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QComboBox, QPushButton, QLabel
from wavegen import generateSamples

tValues = []
yValues = []


class MyPlotWidget(pg.PlotWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setMouseEnabled(x=False, y=False)
        self.setXRange(0, 1)
        self.setYRange(-1, 1)
        self.am_drawing = False

        global tValues, yValues
        self.prevMouseClick = 0

        nextPoint = 0

        while (nextPoint <= 1):
            tValues.append(nextPoint)
            yValues.append(0)
            nextPoint = round(nextPoint + 0.001, 3)

        self.line = self.plot(tValues, yValues, pen='b')

    def mousePressEvent(self, event: QMouseEvent):
        global tValues, yValues
        pos = self.plotItem.vb.mapSceneToView(event.position())

        if event.button().name == 'LeftButton':

            xVal = self.updateX(pos)
            yVal = self.updateY(pos)

            if xVal in tValues:
                yValues[tValues.index(xVal)] = yVal
                self.prevMouseClick = tValues.index(xVal)
                #self.clear()
                #self.line = self.plot(tValues, t=yValues, pen='b')

                self.am_drawing = True

    def mouseMoveEvent(self, event: QMouseEvent):
        global tValues, yValues
        if self.am_drawing:
            pos = self.plotItem.vb.mapSceneToView(event.position())

            xVal = self.updateX(pos)
            yVal = self.updateY(pos)

            currentMouseIndex = tValues.index(xVal)
            if xVal in tValues:
                if (currentMouseIndex - self.prevMouseClick) > 1:

                    # fill in a constant value for the missing samples.
                    while (self.prevMouseClick <= currentMouseIndex + 1):
                        self.prevMouseClick = self.prevMouseClick + 1
                        yValues[self.prevMouseClick] = yVal

                        # tempY = tempY+slope
                if (currentMouseIndex - self.prevMouseClick) < -1:

                    # fill in a constant value for the missing samples.
                    while (self.prevMouseClick >= currentMouseIndex - 1):
                        self.prevMouseClick = self.prevMouseClick - 1
                        yValues[self.prevMouseClick] = yVal

                self.prevMouseClick = currentMouseIndex
                yValues[tValues.index(xVal)] = yVal
                self.clear()
                self.line = self.plot(tValues, yValues, pen='b')

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button().name == 'LeftButton':
            self.am_drawing = False

    def updateX(self, pos):
        pos = str(pos)
        xVal = pos[pos.rfind('(') + 1: pos.rfind(',')]
        xVal = self.truncate(float(xVal), 3)
        return xVal

    def updateY(self, pos):
        pos = str(pos)
        yVal = pos[pos.rfind(',') + 2: pos.rfind(')')]
        yVal = self.truncate(float(yVal), 3)
        return yVal

    def truncate(self, number: float, digits: int) -> float:
        pow10 = 10 ** digits
        return number * pow10 // 1 / pow10

    def setSamples(self, samples):
        global tValues, yValues
        yValues = []
        self.clear()
        for i in range(0, len(tValues)):
            yValues.append(samples[i])
        self.line = self.plot(tValues, yValues, pen='b')


class AppWindow(QtWidgets.QWidget):

    def __init__(self):
        super(AppWindow, self).__init__()
        self.setWindowTitle('Waveform drawer')
        self.waveform_type = 'Line'

        self.pl = MyPlotWidget()
        self.init_dropdown()
        self.init_buttons()
        self.init_connections()

        form = QtWidgets.QFormLayout()

        self.samples = QtWidgets.QLineEdit()
        self.filename = QtWidgets.QLineEdit()
        form.addRow("#Samples:", self.samples)
        form.addRow("Filename:", self.filename)

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(QtWidgets.QLabel("Wave Preset"))
        vert.addWidget(self.dropdown)
        vert.addWidget(self.gen_preset)
        vert.addSpacing(300)
        vert.addLayout(form)
        vert.addWidget(self.generate_csv)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pl)
        layout.addLayout(vert)

        self.setLayout(layout)

    def init_buttons(self):
        self.gen_preset = QPushButton("Generate Preset")
        self.gen_preset.resize(200, 50)
        self.generate_csv = QPushButton("Generate CSV")

    def init_dropdown(self):
        self.dropdown = QComboBox(self)
        self.dropdown.addItem('Line')
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')

    def init_connections(self):
        self.dropdown.activated.connect(lambda: self.update_dropdown())
        self.gen_preset.clicked.connect(self.generate_preset)
        self.generate_csv.clicked.connect(self.save_waveform)

    def update_dropdown(self):
        self.waveform_type = self.dropdown.currentText().lower()

    def generate_preset(self):
        type = self.waveform_type

        if type == "line":
            type = "dc"
        
        res = generateSamples(type = type, numSamples = len(tValues), amplitude = 1)
        samples = res[2]
        self.pl.setSamples(samples)
        
    def save_waveform(self):
        global tValues, yValues


