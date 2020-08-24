""" Screen for the Guitar Suite that shows the user some stats
    about their progress and lets them enter chords they have learned. """

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from chordbuilder import ChordBuilder
import time
from datetime import datetime

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

        self.stats_table = QTableWidget(self)
        self.stats_table.setSortingEnabled(True)
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Chord Pair", "High Score", "Average Score", "Last Played"])

        self.grid.addWidget(self.chord_container, 0, 0)
        self.grid.addWidget(self.instructions, 1, 0)
        self.grid.addWidget(self.chordbuilder, 2, 0)
        self.grid.addWidget(self.stats_table, 0, 1, 3, 1)

        self.init_chords()
        self.display_chords()
        self.load_stats()

    def init_chords(self):
        self.chord_dict = {chord: QLabel(chord) for chord in self.data.chords}

    def clear_chords(self):
        for i in reversed(range(self.chord_grid.count())):
            self.chord_grid.itemAt(i).widget().setParent(None)

    def display_chords(self, num_cols=7):
        for count, chord_label in enumerate(self.chord_dict.values()):
            r, c = count // num_cols, count % num_cols
            self.chord_grid.addWidget(chord_label, r, c)

    def load_stats(self):
        self.stats_table.setRowCount(len(self.data.scores))
        for count, pair in enumerate(self.data.scores):
            key = QTableWidgetItem(", ".join(pair))
            key.setFlags(Qt.ItemIsEnabled)
            high = QTableWidgetItem(str(self.data.highscore(pair)))
            high.setFlags(Qt.ItemIsEnabled)
            avg = QTableWidgetItem(str(self.data.avgscore(pair)))
            avg.setFlags(Qt.ItemIsEnabled)
            latest_time = sorted(list(self.data.scores[pair].keys()))[-1]
            recent = QTableWidgetItem(datetime.fromtimestamp(latest_time).strftime("%y/%m/%d"))
            recent.setFlags(Qt.ItemIsEnabled)
            self.stats_table.setItem(count, 0, key)
            self.stats_table.setItem(count, 1, high)
            self.stats_table.setItem(count, 2, avg)
            self.stats_table.setItem(count, 3, recent)

    def update_chords(self):
        self.clear_chords()
        self.display_chords()

    def submit_chord(self, chord):
        if self.data.add_chord(chord):
            self.chord_dict[chord] = QLabel(chord)
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
