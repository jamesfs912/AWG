import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import subprocess

import sys

class WaveformGenerator(QtWidgets.QWidget):


    def __init__(self):
        super().__init__()
        self.setWindowTitle('Waveform Generator')

        # Initialize variables
        self.fs = 1000
        self.freq = 1
        self.amplitude = 1
        self.phase = 0
        self.offset = 0
        self.waveform_type = 'sine'
        self.arbitrary_waveform = None

        # Create GUI elements
        self.plot_widget = pg.PlotWidget()
        self.plot_data = self.plot_widget.plot(pen='b')
        self.freq_label = QtWidgets.QLabel(f'Frequency (Hz): {self.freq}')
        self.freq_textbox = QtWidgets.QLineEdit(str(self.freq))
        self.amp_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.amp_label = QtWidgets.QLabel(f'Amplitude: {self.amplitude}')
        self.amp_slider.setRange(-5, 5)
        self.amp_slider.setValue(self.amplitude)
        self.offset_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.offset_label = QtWidgets.QLabel(f'Offset voltage: {self.offset}')
        self.offset_slider.setRange(-7, 7)
        self.offset_slider.setValue(self.offset)
        self.sine_button = QtWidgets.QPushButton('Sine')
        self.triangle_button = QtWidgets.QPushButton('Triangle')
        self.square_button = QtWidgets.QPushButton('Square')
        self.sawtooth_button = QtWidgets.QPushButton('Sawtooth')
        self.arb_button = QtWidgets.QPushButton('Arbitrary')
        self.arb_file_label = QtWidgets.QLabel('No file selected')
        self.arb_file_button = QtWidgets.QPushButton('Select file')
        self.generate_button = QtWidgets.QPushButton('Generate')

        # Create layout
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.plot_widget, 0, 0, 4, 4)
        grid_layout.addWidget(self.freq_label, 4, 0)
        grid_layout.addWidget(self.freq_textbox, 4, 1)
        grid_layout.addWidget(self.amp_label, 5, 0)
        grid_layout.addWidget(self.amp_slider, 5, 1)
        grid_layout.addWidget(self.offset_label, 6, 0)
        grid_layout.addWidget(self.offset_slider, 6, 1)
        grid_layout.addWidget(self.sine_button, 4, 2)
        grid_layout.addWidget(self.triangle_button, 4, 3)
        grid_layout.addWidget(self.square_button, 5, 2)
        grid_layout.addWidget(self.sawtooth_button, 5, 3)
        grid_layout.addWidget(self.arb_button, 6, 2)
        grid_layout.addWidget(self.arb_file_label, 6, 3)
        grid_layout.addWidget(self.arb_file_button, 7, 3)
        grid_layout.addWidget(self.generate_button, 7, 0, 1, 2)
        self.setLayout(grid_layout)

        # Connect signals to slots
        self.freq_textbox.textChanged.connect(self.set_frequency)
        self.amp_slider.valueChanged.connect(self.set_amplitude)
        self.offset_slider.valueChanged.connect(self.set_offset)
        self.sine_button.clicked.connect(self.set_sine)
        self.triangle_button.clicked.connect(self.set_triangle)
        self.square_button.clicked.connect(self.set_square)
        self.sawtooth_button.clicked.connect(self.set_sawtooth)
        self.arb_button.clicked.connect(self.set_arbitrary)
        self.arb_file_button.clicked.connect(self.select_arbitrary_file)
        self.generate_button.clicked.connect(self.generate_waveform)

    def set_frequency(self, text):
        if text.isnumeric():
            self.freq = int(text)
        else:
            self.freq = 0
        self.freq_label.setText(f'Frequency (Hz): {self.freq}')

    def set_amplitude(self, value):
        self.amplitude = value
        self.amp_label.setText(f'Amplitude: {self.amplitude}')

    def set_offset(self, value):
        self.offset = value
        self.offset_label.setText(f'Offset voltage: {self.offset}')

    def set_sine(self):
        self.waveform_type = 'sine'

    def set_triangle(self):
        self.waveform_type = 'triangle'

    def set_square(self):
        self.waveform_type = 'square'

    def set_sawtooth(self):
        self.waveform_type = 'sawtooth'

    def set_arbitrary(self):
        self.waveform_type = 'arbitrary'

    def select_arbitrary_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('csv files (*.csv)')
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.arb_file_label.setText(file_path)
            self.arbitrary_waveform = np.loadtxt(file_path)

    def load_arbitrary_waveform(self):
        try:
            # Read the CSV file and update the waveform data
            self.arbitrary_waveform = np.genfromtxt('AWG.csv', delimiter='\n')
            self.generate_waveform()
        except OSError:
            pg.QtGui.QMessageBox.warning(self, 'Error', 'Failed to read arbitrary waveform data')

    def generate_waveform(self):
        if self.waveform_type == 'sine':
            t = np.linspace(0, 1, self.fs, endpoint=False)
            y = self.amplitude * np.sin(2 * np.pi * self.freq * t + np.deg2rad(self.phase))+self.offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'triangle':
            t = np.linspace(0, 1, self.fs, endpoint=False)
            y = self.amplitude * (2 / np.pi * np.arcsin(np.sin(2 * np.pi * t * self.freq + np.deg2rad(self.phase))))+self.offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'square':
            t = np.linspace(0, 1, self.fs, endpoint=False)
            y = self.amplitude * np.where(np.mod(np.floor(2 * self.freq * t + 2 * self.phase / 360.0), 2) == 0, -1, 1)+self.offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'sawtooth':
            t = np.linspace(0, 1, self.fs, endpoint=False)
            y = self.amplitude * (2 / np.pi * np.arctan(np.tan(np.pi * t * self.freq + np.deg2rad(self.phase))))+self.offset
            self.plot_data.setData(t, y, pen='y')
        elif self.waveform_type == 'arbitrary' and self.arbitrary_waveform is not None:
            t = np.linspace(0, 1, len(self.arbitrary_waveform), endpoint=False)
            y = self.amplitude * self.arbitrary_waveform+self.offset
            self.plot_data.setData(t, y, pen='y')
        else:
            pg.QtWidgets.QMessageBox.warning(self, 'Error', 'No arbitrary waveform file selected')

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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    waveform_generator = WaveformGenerator()
    waveform_generator.show()
    sys.exit(app.exec())
