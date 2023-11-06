import pyqtgraph as pg
from PyQt6 import QtWidgets
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QComboBox, QPushButton

from channal import Channal
from aw import AW
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
        while nextPoint <= 1:
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
                yValues[int(xVal * 1000)] = yVal
                self.prevMouseClick = int(xVal * 1000)
                # self.clear()
                # self.line = self.plot(tValues, t=yValues, pen='b')

                self.am_drawing = True

    def mouseMoveEvent(self, event: QMouseEvent):
        global tValues, yValues
        pos = self.plotItem.vb.mapSceneToView(event.position())

        xVal = self.updateX(pos)
        yVal = self.updateY(pos)
        if self.am_drawing and xVal >= 0 and xVal <= 1:

            if xVal in tValues and self.prevMouseClick < len(tValues):

                currentMouseIndex = int(xVal * 1000)
                y = yVal - yValues[self.prevMouseClick]
                x = currentMouseIndex - self.prevMouseClick
                if x != 0:
                    slope = (y / x)
                else:
                    slope = y
                count = 1
                yStart = yValues[self.prevMouseClick]

                if (currentMouseIndex - self.prevMouseClick) > 1:

                    # fill in a constant value for the missing samples.
                    while self.prevMouseClick <= currentMouseIndex + 1 and self.prevMouseClick < len(tValues) - 1:
                        self.prevMouseClick = self.prevMouseClick + 1
                        yValues[self.prevMouseClick] = yStart + count * slope
                        count = count + 1

                        # tempY = tempY+slope
                if (currentMouseIndex - self.prevMouseClick) < -1 and self.prevMouseClick < len(tValues) - 1:

                    # fill in a constant value for the missing samples.
                    while self.prevMouseClick >= currentMouseIndex - 1 and self.prevMouseClick < len(tValues) - 1:
                        self.prevMouseClick = self.prevMouseClick - 1
                        yValues[self.prevMouseClick] = yVal

                self.prevMouseClick = currentMouseIndex
                yValues[int(xVal * 1000)] = yVal
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

    @staticmethod
    def truncate(number: float, digits: int) -> float:
        pow10 = 10 ** digits
        return number * pow10 // 1 / pow10

    def setSamples(self, samples):
        global tValues, yValues
        yValues = []
        self.clear()
        for i in range(0, len(tValues)):
            yValues.append(samples[i])
        self.line = self.plot(tValues, yValues, pen='b')

    @staticmethod
    def return_samples():
        temp = []
        for i in range(0, len(tValues)):
            temp.append(yValues[i])
        return temp


class AppWindow(QtWidgets.QWidget):

    def __init__(self, channel1, channel2):
        super(AppWindow, self).__init__()

        self.channel2 = channel2
        self.channel1 = channel1
        self.setWindowTitle('Waveform drawer')
        self.waveform_type = 'Line'

        self.listAW = []

        self.pl = MyPlotWidget()
        self.init_dropdown()
        self.init_buttons()
        self.init_connections()

        #listAW initialized with dropdown
        self.channel1.updateAWList(self.listAW)
        self.channel2.updateAWList(self.listAW)

        form = QtWidgets.QFormLayout()

        self.filename = QtWidgets.QLineEdit()
        form.addRow("Filename:", self.filename)

        vert = QtWidgets.QVBoxLayout()
        vert.addWidget(QtWidgets.QLabel("Wave Preset"))
        vert.addWidget(self.dropdown)
        vert.addWidget(self.gen_preset)
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

        self.addWave_button = QPushButton("Add Wave")
        self.addWave_button.resize(200, 50)

        self.delWave_button = QPushButton("Delete Wave")
        self.delWave_button.resize(200, 50)

        self.loadWave_button = QPushButton("Load Wave")
        self.loadWave_button.resize(200, 50)

    def init_dropdown(self):
        self.dropdown = QComboBox(self)
        self.dropdown.addItem('Line')
        self.dropdown.addItem('Sine')
        self.dropdown.addItem('Triangle')
        self.dropdown.addItem('Sawtooth')
        self.dropdown.addItem('Square')

        self.stored_waves = QComboBox(self)
        f = open("saved.txt", "r")
        for line in f:
            self.stored_waves.addItem(line[0: line.find(',')])
            strArray = line[line.find('[') + 1: len(line) - 2]
            strArray = strArray.split(", ")
            arr = [float(val) for val in strArray]

            self.listAW.append(AW(line[0: line.find(',')], arr))

    def init_connections(self):
        self.dropdown.activated.connect(lambda: self.update_dropdown())
        self.gen_preset.clicked.connect(self.generate_preset)

        self.addWave_button.clicked.connect(self.addAW)
        self.delWave_button.clicked.connect(self.deleteAW)
        self.loadWave_button.clicked.connect(self.load_wave)

    def update_dropdown(self):
        self.waveform_type = self.dropdown.currentText().lower()

    def generate_preset(self):
        type = self.waveform_type

        if type == "line":
            type = "dc"

        res = generateSamples(type=type, numSamples=len(tValues), amplitude=1)
        samples = res[2]
        self.pl.setSamples(samples)

    # functions for new method of saving drawn waves

    def load_wave(self):
        global tValues, yValues
        yValues = []
        for a in self.listAW:

            if a.filename == self.stored_waves.currentText():
                self.pl.clear()
                for i in range(0, len(tValues)):
                    yValues.append(a.samples[i])
                self.pl.line = self.pl.plot(tValues, yValues, pen='b')

    def addAW(self):

        temp = self.pl.return_samples()
        self.stored_waves.addItem(self.filename.text())
        self.listAW.append(AW(self.filename.text(), temp))

        self.generate_listAW_file()

        self.channel1.updateAWList(self.listAW)
        self.channel2.updateAWList(self.listAW)

    def deleteAW(self):
        for a in self.listAW:
            if a.filename == self.stored_waves.currentText():
                self.listAW.remove(a)
        self.stored_waves.removeItem(self.stored_waves.currentIndex())

        self.generate_listAW_file()
        self.channel1.updateAWList(self.listAW)
        self.channel2.updateAWList(self.listAW)

    def generate_listAW_file(self):

        with open('saved.txt', 'w', newline='') as f:
            for i in self.listAW:
                f.write(i.filename + ", " + str(i.samples))
                f.write('\n')

