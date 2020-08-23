""" Screen for the Guitar Suite that shows the user some stats
    about their progress and lets them enter chords they have learned. """

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout
from chordbuilder import ChordBuilder

class UserProgress(QWidget):

    def __init__(self, data, *args, **kwargs):
        super(UserProgress, self).__init__(*args, **kwargs)
        self.data = data
        self.grid = QGridLayout(self)

        self.instructions = QLabel("You can add chords here")
        self.chord_container = QWidget()
        self.chord_grid = QGridLayout(self.chord_container)
        self.chordbuilder = ChordBuilder()
        self.chordbuilder.submit.connect(self.submit_chord)

        self.grid.addWidget(self.chord_container, 0, 0)
        self.grid.addWidget(self.instructions, 1, 0)
        self.grid.addWidget(self.chordbuilder, 2, 0)

        self.init_chords()
        self.display_chords()

    def init_chords(self):
        self.chord_labels = {chord: QLabel(chord) for chord in self.data.chords}

    def clear_chords(self):
        for i in reversed(range(self.chord_grid.count())):
            self.chord_grid.itemAt(i).widget().setParent(None)

    def display_chords(self, num_cols=7):
        for count, chord_label in enumerate(self.chord_labels.values()):
            r, c = count // num_cols, count % num_cols
            self.chord_grid.addWidget(chord_label, r, c)

    def update_chords(self):
        self.clear_chords()
        self.display_chords()

    def submit_chord(self, chord):
        if self.data.add_chord(chord):
            self.chord_labels[chord] = QLabel(chord)
            self.update_chords()
        else:
            self.instructions.setText("Chord was not added.")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from chorddata import ChordData
    c = ChordData("mychords.txt")
    a = QApplication([])
    p = UserProgress(c)
    p.show()
    a.exec_()
