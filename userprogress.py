""" Screen for the Guitar Suite that shows the user some stats
    about their progress and lets them enter chords they have learned. """

import chorddata
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication
from chordbuilder import ChordBuilder

class Progress(QWidget):

    def __init__(self, *args, **kwargs):
        super(Progress, self).__init__(self, *args, **kwargs)
        self.grid = QGridLayout(self)
