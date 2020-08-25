""" Screen for the Guitar Suite that shows the user some stats
    about their progress and lets them enter chords they have learned. """

from PyQt5.QtCore import Qt, pyqtSignal, QVariant
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit
from chordbuilder import ChordBuilder
import time
from datetime import datetime

class UserProgress(QWidget):

    def __init__(self, data, *args, **kwargs):
        super(UserProgress, self).__init__(*args, **kwargs)
        self.data = data
        # NOTE : change the name of this if you stick with vbox instead of grid
        self.grid = QHBoxLayout(self)

        self.chord_side = QWidget()
        self.chord_vbox = QVBoxLayout(self.chord_side)

        self.stats_side = QWidget()
        self.stats_vbox = QVBoxLayout(self.stats_side)

        known_chords = QLabel("My Chords")
        known_chords.setProperty("font-class", "h3")
        self.chord_container = QWidget()
        self.chord_grid = QGridLayout(self.chord_container)
        self.instructions = QLabel("Add Chords")
        self.instructions.setProperty("font-class", "instructions")
        self.instructions.setAlignment(Qt.AlignBottom)
        self.chord_entry = QLineEdit()
        self.submit_button = QPushButton("Add Chord")
        self.submit_button.clicked.connect(self.submit_chord)
        #self.chordbuilder = ChordBuilder()
        #self.chordbuilder.submit.connect(self.submit_chord)

        table_label = QLabel("60 Second Chord Change Stats")
        table_label.setProperty("font-class", "h3")
        self.stats_table = QTableWidget(self)
        self.stats_table.setSortingEnabled(True)
        self.stats_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["Chord Pair", "High Score", "Average Score", "Last Played"])
        self.stats_table.setMinimumWidth(450)
        self.stats_table.setMaximumWidth(450)

        #self.grid.addWidget(known_chords, 0, 0, 1, 2)
        #self.grid.addWidget(self.chord_container, 1, 0, 1, 2)
        #self.grid.addWidget(self.instructions, 2, 0, 1, 2)
        #self.grid.addWidget(self.chord_entry, 3, 0)
        #self.grid.addWidget(self.submit_button, 3, 1)
        #self.grid.addWidget(table_label, 0, 2, 1, 2)
        #self.grid.addWidget(self.stats_table, 1, 2, 4, 2)
        self.chord_vbox.addWidget(known_chords)
        self.chord_vbox.addWidget(self.chord_container)
        self.chord_vbox.addWidget(self.instructions)
        self.chord_vbox.addWidget(self.chord_entry)
        self.chord_vbox.addWidget(self.submit_button)
        self.chord_vbox.setAlignment(Qt.AlignCenter)
        self.stats_vbox.addWidget(table_label)
        self.stats_vbox.addWidget(self.stats_table)
        self.stats_vbox.setAlignment(Qt.AlignCenter)

        self.grid.addWidget(self.chord_side)
        self.grid.addWidget(self.stats_side)
        #self.grid.setAlignment(Qt.AlignCenter)

        self.init_chords()
        self.display_chords()
        self.display_stats()

    def init_chords(self):
        self.chord_dict = {}
        for chord in self.data.chords:
            chord_button = QPushButton(chord)
            chord_button.setProperty("id", "chord-button")
            self.chord_dict[chord] = chord_button

    def clear_chords(self):
        for i in reversed(range(self.chord_grid.count())):
            self.chord_grid.itemAt(i).widget().setParent(None)

    def display_chords(self, num_cols=5):
        for count, chord_label in enumerate(self.chord_dict.values()):
            r, c = count // num_cols, count % num_cols
            self.chord_grid.addWidget(chord_label, r, c)

    def clear_stats(self):
        for r in range(self.stats_table.rowCount()):
            for c in range(self.stats_table.columnCount()):
                self.stats_table.item(r, c).setParent(None)


    def display_stats(self):
        self.stats_table.setRowCount(len(self.data.scores))
        for count, pair in enumerate(self.data.scores):
            key = QTableWidgetItem(", ".join(pair))
            key.setFlags(Qt.ItemIsEnabled)
            # The table items that hold integers (high and avg) use QVariant(int)
            # and the Qt.EditRole (or Qt.DisplayRole, they are the same for TableWidgetItem.setData())
            # to display and sort the values as integers instead of strings.
            high = QTableWidgetItem()
            high.setData(Qt.EditRole, QVariant(self.data.highscore(pair)))
            high.setFlags(Qt.ItemIsEnabled)
            avg = QTableWidgetItem()
            avg.setData(Qt.EditRole, QVariant(self.data.avgscore(pair)))
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

    def submit_chord(self, garbage):
        """
            Get the text from self.chord_entry
            garbage is a throwaway arg from PushButton.clicked signal
        """
        chord = self.chord_entry.text()
        if chord_added := self.data.add_chord(chord):
            chord_button = QPushButton(chord)
            chord_button.setProperty("id", "chord-button")
            self.chord_dict[chord] = chord_button
            self.update_chords()
            self.display_stats()
            self.instructions.setText(f"'{chord}' added.")
        elif chord_added == False:
            self.instructions.setText(f"'{chord}' was not added. It is a duplicate.")
        elif chord_added == None:
            self.instructions.setText(f"'{chord}' was not added. It did not pass the inspection.")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from chorddata import ChordData
    c = ChordData("mychords.txt")
    a = QApplication([])
    p = UserProgress(c)
    p.show()
    a.exec_()
