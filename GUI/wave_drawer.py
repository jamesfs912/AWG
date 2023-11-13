import pyqtgraph as pg
import os
from PyQt6 import QtWidgets
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QComboBox, QPushButton, QLineEdit, QMessageBox
from wavegen import generateSamples, resample, sample
import numpy as np
import math
from random import random
from PyQt6 import QtGui, QtCore

SAMPLE_POINTS = 1024*4
ICON_SIZE = 64

class AW:
    def __init__(self, name, samples):
        """Creates an arbritary wave with the given name and samples."""
        self.name = name
        self.samples = samples
        self.icon = None
        if self.samples == None:
            self.samples = [0] * SAMPLE_POINTS
        self.genIcon()
            
    def lineDraw(self, map, x1, y1, x2, y2):   
        """
        Draws a line on the given map from (x1, y1) to (x2, y2).
        """
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) > abs(dy):
            steps = abs(dx)
        else:
            steps = abs(dy)
        xincrement = dx/steps
        yincrement = dy/steps
        i = 0
        while i < steps:
            i +=1
            x1 = x1 + xincrement
            y1 = y1 + yincrement
            brush = 1
            _x = int(max(x1 - brush, 0))
            while _x < min(x1 + 1 + brush, ICON_SIZE - 1):
                _y = int(max(y1 - brush, 0))
                while _y < min(y1 + 1 + brush, ICON_SIZE - 1):
                    map[(_y * ICON_SIZE + _x) * 3 + 0] = 0
                    map[(_y * ICON_SIZE + _x) * 3 + 1] = 255
                    map[(_y * ICON_SIZE + _x) * 3 + 2] = 255
                    _y += 1
                _x += 1
                
    def genIcon(self):
        """
        Generates an icon for the wave.
        """
        map =  [255]*(ICON_SIZE*ICON_SIZE * 3)
        last = None
        for x in range(ICON_SIZE):
            y = -sample(self.samples, x / ICON_SIZE) * ICON_SIZE / 2+ ICON_SIZE / 2
            y = max(min(y, ICON_SIZE - 1), 0)
            if last:
                self.lineDraw(map, last[0], last[1], x, y)
            last = (x, y)
        self.icon = QtGui.QIcon(QtGui.QPixmap(QtGui.QImage(bytes(map), ICON_SIZE, ICON_SIZE,   QtGui.QImage.Format.Format_RGB888)))
        return
            
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
        """
        Handles the mouse press event for the wave drawer..
        """
        if event.button().name == 'LeftButton':
            pos = self.plotItem.vb.mapSceneToView(event.position())
            
            self.lastX = round(pos.x() * SAMPLE_POINTS)
            self.lastY = pos.y()
            self.am_drawing = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handles the mouse release event for the wave drawer.
        """
        if event.button().name == 'LeftButton' and self.am_drawing:
            pos = self.plotItem.vb.mapSceneToView(event.position())
            self.movedPen(pos)
            self.am_drawing = False
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handles the mouse move event for the wave drawer.
        """
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
        res = generateSamples(wavetype=type, numSamples=SAMPLE_POINTS, amplitude=1)
        self.valuesY = res[1]
        self.updateGraph()

    def setSamples(self, samples):
        """
        Sets the list of samples to the given list.

        Parameters:
            samples (list): The list of samples
        """
        self.valuesY = samples
        self.updateGraph()

    def return_samples(self):
        """
        Returns the list of samples.
        
        Returns:
            list: The list of samples
        """
        temp = []
        for i in range(0, len(self.valuesX)):
            temp.append(self.valuesY[i])
        return self.valuesY.copy()
    
class AppWindow(QtWidgets.QWidget):

    def __init__(self, chans):
        """
        Initializes the wave drawer window with the given channels. 
        
        Parameters:
            chans (list): The list of channels to update when a wave is modified
        """
        super(AppWindow, self).__init__()

        self.chans = chans
        self.setWindowTitle('Waveform drawer')
        self.currently_loaded_wave = None

        self.listAW = []

        self.pl = MyPlotWidget()
        
        
        self.stored_waves = QComboBox(self)
        self.stored_waves.currentIndexChanged.connect(self.dropDownIndexChanged)
        self.stored_waves.view().setIconSize(QtCore.QSize(ICON_SIZE,ICON_SIZE))

        self.dropdown = QComboBox(self)
        self.dropdown.addItem('DC')
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')
        
        self.gen_preset = QPushButton("Generate Preset")
        self.gen_preset.resize(200, 50)
        self.gen_preset.clicked.connect(lambda: self.pl.generate_preset(self.dropdown.currentText().lower()))
        
        self.code_input = QLineEdit  ("rand * 0.1 + sin(x*2*pi)*0.5")

        self.gen_code = QPushButton("Generate Code")
        self.gen_code.resize(200, 50)
        self.gen_code.clicked.connect(lambda: self.pl.generate_code(self.code_input.text()))
 
        self.saveWaveButton = QPushButton("Save Wave")
        self.saveWaveButton.resize(200, 50)
        self.saveWaveButton.clicked.connect(self.saveFunction)

        self.delWave_button = QPushButton("Delete")
        self.delWave_button.resize(200, 50)
        self.delWave_button.clicked.connect(self.delButtonClicked)
        
        self.newWaveButtpm = QPushButton("Add new")
        self.newWaveButtpm.resize(200, 50)
        self.newWaveButtpm.clicked.connect(lambda: (self.addWave(), self.updateDropDown(), self.stored_waves.setCurrentIndex(len(self.listAW) - 1)))

        self.nameEdit = QLineEdit()
        self.nameEdit.editingFinished.connect(self.nameEditDone)

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(QtWidgets.QLabel("Wave Preset"))
        vert.addWidget(self.dropdown)
        vert.addWidget(self.gen_preset)
        vert.addWidget(self.code_input)
        vert.addWidget(self.gen_code)
        vert.addSpacing(300)
        vert.addWidget(QtWidgets.QLabel("Select"))
        vert.addWidget(self.stored_waves)
        vert.addWidget(self.newWaveButtpm)

        vert.addWidget(QtWidgets.QLabel("Edit name:"))
        vert.addWidget(self.nameEdit)
        
        vert.addWidget(self.saveWaveButton)
        vert.addWidget(self.delWave_button)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pl)
        layout.addLayout(vert)

        self.setLayout(layout)
        self.loadFile()

    def dropDownIndexChanged(self, ind):
        if ind == -1:
            return
        self.nameEdit.setText(self.listAW[ind].name)
        self.pl.setSamples(self.listAW[ind].samples.copy())

    def nameEditDone(self):
        self.listAW[self.stored_waves.currentIndex()].name = self.nameEdit.text()
        self.updateDropDown()

    def saveFunction(self):
        """
        Saves the current wave to the list and generates an icon for it.
        """
        self.listAW[self.stored_waves.currentIndex()].samples = self.pl.valuesY.copy()
        self.listAW[self.stored_waves.currentIndex()].genIcon()
        #for c in self.chans:
        #    c.updateAWList(self.listAW, )
        #self.saveFile()
        self.updateDropDown(cause = "mod", modified = self.stored_waves.currentIndex())
        
    def updateDropDown(self, cause = "", modified = -1):
        """
        Updates the drop down list of waves.

        Parameters:
            cause (str): The cause of the update, can be "mod" for modified, "del" for deleted or "" for other
            modified (int): The index of the modified wave, -1 if no wave was modified
        """
        ind = self.stored_waves.currentIndex()
        self.stored_waves.clear()
        i = 0
        for aw in self.listAW:
            self.stored_waves.addItem(aw.name)
            if aw.icon:
                self.stored_waves.setItemIcon(i, aw.icon)
                i += 1
        l = len(self.listAW)
        self.delWave_button.setEnabled(l > 1)
        if l > 0 and ind != -1:
            self.stored_waves.setCurrentIndex(min(ind, l - 1))
        for c in self.chans:
            c.updateAWList(self.listAW, cause, modified)
        self.saveFile()
    
    def saveFile(self):   
        with open('saved.txt', 'w') as f:  # Open in 'w' mode to overwrite the file
            for aw in self.listAW:
                #f.write(aw.filename + ":" + str(aw.samples) + '\n')
                f.write(aw.name + ":")
                for i in range(len(aw.samples)):
                    f.write(str(aw.samples[i]))
                    if i != len(aw.samples) - 1:
                        f.write(",")
                f.write("\n") 
                
    def nameUsed(self, name):
        """
        Checks if the name is already used

        Parameters:
            name (str): The name to check

        Returns:
            bool: True if the name is already used, False otherwise
        """
        for aw in self.listAW:
            if aw.name == name:
                return True
        return False
        
    def addWave(self, name = None, arr = None):
        """
        Adds a new wave to the list.

        Parameters:
            name (str): The name of the wave. If None, a default name is used
            arr (list): The list of samples. If None, a default list is used

        Returns:
            None
        """
        if name == None:
            num = 0
            while True:
                s = "Custum " + str(num)
                num += 1
                if not self.nameUsed(s):
                    name = s
                    break
        self.listAW.append(AW(name, arr))
        
    def loadFile(self):
        """
        Loads the saved waves from the file, if there are no saved waves, a default wave is added.

        Parameters:
            None

        Returns:
            None
        """
        if os.path.exists("saved.txt"):
        # Check if saved.txt exists and create it if it doesn't
        #    with open("saved.txt", "w") as f: #this would end up being done later
        #        pass
        #else:
            with open("saved.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    name = line[: line.find(':')]
                    strArray = line[line.find(':') + 1:]
                    strArray = strArray.split(",")
                    arr = [float(val) for val in strArray]
                    self.addWave(name, arr)
        if len(self.listAW) == 0:
            self.addWave()
        self.updateDropDown()
            
    def delButtonClicked(self):
        """
        Deletes the currently selected wave.

        Parameters:
            None
        
        Returns:
            None
        """
        ind = self.stored_waves.currentIndex()
        del self.listAW[ind]
        self.updateDropDown(cause = "del",  modified = ind)