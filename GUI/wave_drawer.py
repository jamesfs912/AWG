import pyqtgraph as pg
import os
from PyQt6 import QtWidgets
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QComboBox, QPushButton, QLineEdit, QMessageBox

from channal import Channal
from wavegen import generateSamples, resample
import numpy as np
import math
from random import random

SAMPLE_POINTS = 1024*4

class MyPlotWidget(pg.PlotWidget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setMouseEnabled(x=False, y=False)
        self.setXRange(0, 1)
        self.setYRange(-1, 1)
        self.am_drawing = False

        self.line = self.plot([], [], pen='c')
        self.valuesX = np.linspace(0, 1, SAMPLE_POINTS, endpoint=False)
        self.valuesY = [0] * SAMPLE_POINTS
        self.updateGraph()
        
    def updateGraph(self):
        self.line.setData(self.valuesX, self.valuesY)

    def movedPen(self, pos):
        newX = round(pos.x() * SAMPLE_POINTS)
        newY = pos.y()
        
        posX = self.lastX
        posY = self.lastY
        dirX = 1 if newX > posX else -1
        if newX != self.lastX:
            dirY = (newY - self.lastY) / (newX - self.lastX) * dirX
        else:
            dirY = 0
        
        while posX != newX + dirX:
            if posX >= 0 and posX < SAMPLE_POINTS:
                self.valuesY[posX] = max(min(posY, 1), -1)
            posX += dirX
            posY += dirY
        
        self.lastX = newX
        self.lastY = newY
        self.updateGraph()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button().name == 'LeftButton':
            pos = self.plotItem.vb.mapSceneToView(event.position())
            
            self.lastX = round(pos.x() * SAMPLE_POINTS)
            self.lastY = pos.y()
            self.am_drawing = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button().name == 'LeftButton' and self.am_drawing:
            pos = self.plotItem.vb.mapSceneToView(event.position())
            self.movedPen(pos)
            self.am_drawing = False
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.am_drawing:
            pos = self.plotItem.vb.mapSceneToView(event.position())
            self.movedPen(pos)
    
    # -"how much security vunrability do you want?"
    # -"yes"
    def generate_code(self, code):
        try:
            tempY = self.valuesY
            env = {}
            env["locals"]   = None
            env["globals"]  = None
            env["__name__"] = None
            env["__file__"] = None
            env["__builtins__"] = None
            env["math"] = math
            for funct in dir(math):
                if funct[0] != '_':
                    env[funct] = getattr(math, funct)
            for i in range(SAMPLE_POINTS):
                env["x"] = i / SAMPLE_POINTS
                env["rand"] = random()*2-1 
                y = eval(code, env)
                tempY[i] = max(min(y, 1), -1)
        except Exception as e:
            print(e)
            return
        self.valuesY = tempY
        self.updateGraph()

    def generate_preset(self, type):
        res = generateSamples(type=type, numSamples=SAMPLE_POINTS, amplitude=1)
        samples = res[2]
        self.valuesY = samples
        self.updateGraph()

    def return_samples(self):
        temp = []
        for i in range(0, len(self.valuesX)):
            temp.append(self.valuesY[i])
        return temp


class AppWindow(QtWidgets.QWidget):

    def __init__(self, channel1, channel2):
        super(AppWindow, self).__init__()

        self.channel2 = channel2
        self.channel1 = channel1
        self.setWindowTitle('Waveform drawer')
        self.currently_loaded_wave = None

        self.listAW = []

        self.pl = MyPlotWidget()
        self.init_dropdown()
        self.init_buttons()
        self.init_connections()
        self.create_file()

        #listAW initialized with dropdown
        self.channel1.updateAWList(self.listAW)
        self.channel2.updateAWList(self.listAW)

        form = QtWidgets.QFormLayout()

        self.filename = QLineEdit()
        form.addRow("Filename:", self.filename)

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(QtWidgets.QLabel("Wave Preset"))
        vert.addWidget(self.dropdown)
        vert.addWidget(self.gen_preset)
        vert.addWidget(self.code_input)
        vert.addWidget(self.gen_code)
        vert.addSpacing(300)
        vert.addWidget(QtWidgets.QLabel("Load/Delete Wave"))
        vert.addWidget(self.stored_waves)
        vert.addWidget(self.loadWave_button)

        vert.addLayout(form)
        vert.addWidget(self.addWave_button)
        vert.addWidget(self.delWave_button)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pl)
        layout.addLayout(vert)

        self.setLayout(layout)

    def init_buttons(self):
        self.gen_preset = QPushButton("Generate Preset")
        self.gen_preset.resize(200, 50)

        self.code_input = QLineEdit  ("rand * 0.1 + sin(x*2*pi)*0.5")
        #self.code_input.setFixedHeight(50)

        self.gen_code = QPushButton("Generate Code")
        self.gen_code.resize(200, 50)

        self.addWave_button = QPushButton("Save Wave")
        self.addWave_button.resize(200, 50)

        self.delWave_button = QPushButton("Delete Wave")
        self.delWave_button.resize(200, 50)

        self.loadWave_button = QPushButton("Load Wave")
        self.loadWave_button.resize(200, 50)

    def init_dropdown(self):
        self.dropdown = QComboBox(self)
        self.dropdown.addItem('DC')
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')

        self.stored_waves = QComboBox(self)
        with open("saved.txt", "r") as f:
            for line in f:
                self.stored_waves.addItem(line[0: line.find(',')])
                strArray = line[line.find('[') + 1: len(line) - 2]
                strArray = strArray.split(", ")
                arr = [float(val) for val in strArray]

                self.listAW.append(AW(line[0: line.find(',')], arr))

    def init_connections(self):
        self.gen_preset.clicked.connect(lambda: self.pl.generate_preset(self.dropdown.currentText().lower()))
        #self.gen_code.clicked.connect(lambda: self.pl.generate_code(self.code_input.toPlainText()))
        self.gen_code.clicked.connect(lambda: self.pl.generate_code(self.code_input.text()))

        self.addWave_button.clicked.connect(self.addAW)
        self.delWave_button.clicked.connect(self.deleteAW)
        self.loadWave_button.clicked.connect(self.load_wave)

    # functions for new method of saving drawn waves

    def create_file(self):
        # Check if saved.txt exists and create it if it doesn't
        if not os.path.exists("saved.txt"):
            with open("saved.txt", "w") as f:
                pass

    def load_wave(self):
        selected_wave_name = self.stored_waves.currentText()
        self.currently_loaded_wave = selected_wave_name
        self.filename.setText(selected_wave_name)
        yValues = []
        for a in self.listAW:
            if a.filename == selected_wave_name:
                for i in range(0, SAMPLE_POINTS):
                    yValues.append(a.samples[i])
                #elf.pl.valuesY = resample(yValues, SAMPLE_POINTS)
                self.pl.valuesY = yValues
                self.pl.updateGraph()

    def addAW(self):
        new_filename = self.filename.text().strip()  # Strip to remove any leading/trailing spaces
        temp = self.pl.return_samples()

        # Check if the user is editing a loaded wave
        if self.currently_loaded_wave == new_filename:
            # Update the existing wave
            for aw in self.listAW:
                if aw.filename == new_filename:
                    aw.samples = temp
                    break
        elif not any(aw.filename == new_filename for aw in self.listAW):
            # Add a new wave
            self.listAW.append(AW(new_filename, temp))
            self.stored_waves.addItem(new_filename)
        else:
            # Error message for a wave name that already exists
            msg = QMessageBox()
            msg.setWindowTitle("Duplicate Name")
            msg.setText("A wave with this name already exists.")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
            return  # Early return to avoid further processing

        self.generate_listAW_file()
        self.channel1.updateAWList(self.listAW)
        self.channel2.updateAWList(self.listAW)


    def deleteAW(self):
        wave_to_delete = self.stored_waves.currentText()
        self.listAW = [aw for aw in self.listAW if aw.filename != wave_to_delete]
        self.stored_waves.removeItem(self.stored_waves.currentIndex())

        self.generate_listAW_file()
        self.channel1.updateAWList(self.listAW)
        self.channel2.updateAWList(self.listAW)

    def generate_listAW_file(self):
        with open('saved.txt', 'w') as f:  # Open in 'w' mode to overwrite the file
            for aw in self.listAW:
                f.write(aw.filename + ", " + str(aw.samples) + '\n')

class AW:
    def __init__(self, filename, samples):
        self.filename = filename
        self.samples = samples

