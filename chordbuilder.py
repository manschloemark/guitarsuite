""" Widget that lets the user build a chord one part at a time """

import chorddata
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class ChordBuilder(QWidget):
    """ Responsive widget that lets a user build chords by pressing buttons.
        Currently only works for 'beginner' level chords, but will be updted """

    # NOTE The way this will work is you click a button from each row
    # to build a chord.
    # there will be a label at the top that changes as the user presses buttons.
    # Pressing two buttons on the same row will cause the 2nd button to replace
    # the first
    # I was going to have the buttons dynamically enable and disable when clickin
    # the button would result in a chord that is already known, but that will
    # cause a lot of problems now that I think about it. I'll just make the
    # GUI tell the user when they try to add a duplicate
    # Each button I make in the loop needs to have a function connected
    # that changes the appropriate part of the chord.
    # 
    # Also, users should be able to type chords in. I'm only making this
    # ChordBuilder for fun really.

    # TODO
    # Learn more about music theory and add logic that prevents nonexistant chords
    # ex: from wikipedia, only 2nd, 3rd, 6th, and 7th chords can be major or minor (and some caveats that are even further beyond me)

    # I figure that storing a list of all valid chords is a better solution.
    # I just enjoy making stuff like this

    submit = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(ChordBuilder, self).__init__(*args, **kwargs)
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignCenter)

        controls = QWidget()
        self.control_hbox = QHBoxLayout(controls)
        self.chord_label = QLabel("Build a chord")
        self.add_chord = QPushButton("Add Chord")
        self.add_chord.clicked.connect(lambda: self.submit.emit(self.chord))

        self.control_hbox.addWidget(self.chord_label)
        self.control_hbox.addWidget(self.add_chord)


        # I do not know the proper terminology for these... things? Chord descriptors?
        keys = "A B C D E F G".split()
        #pitches = ("\u266E", "\u266F", "\u266D") # UTF8 characters for natural, sharp, and flat. I do not use them because it complicates the regex.
        pitches = "b Natural #".split()
        #qualities = "Maj min dim sus ".split() # For now I won't include dim and sus
        qualities = "Maj min".split()
        intervals = "2 3 4 5 6 7 9 11 13".split()

        self.vbox.addWidget(controls)

        for func, group in zip((self.set_key, self.set_pitch, self.set_quality, self.set_interval), (keys, pitches, qualities, intervals)):
            row = QWidget()
            hbox = QHBoxLayout(row)
            for char in group:
                button = QPushButton(char)
                hbox.addWidget(button)
                button.clicked.connect(lambda x, func=func, char=char: func(char))
            self.vbox.addWidget(row)

        self.reset_chord()

    @property
    def chord(self):
        return f"{self.key}{self.pitch}{self.quality}{self.interval}"

    def reset_chord(self):
        self.key, self.pitch, self.quality, self.interval = '', '', '', ''
        self.update_label()

    def set_key(self, key):
        if key == self.key:
            self.key = ''
        else:
            self.key = key
        self.update_label()

    def set_pitch(self, pitch):
        if pitch == self.pitch or pitch == 'Natural':
            self.pitch = ''
        else:
            self.pitch = pitch
        self.update_label()

    def set_interval(self, interval):
        if interval == self.interval:
            self.interval = ''
        else:
            self.interval = interval
        self.update_label()

    def set_quality(self, quality):
        if quality == self.quality or quality == 'Maj':
            self.quality = ''
        else:
            if quality == 'min':
                self.quality = 'm'
            else:
                self.quality = quality
        self.update_label()

    def update_label(self):
        self.chord_label.setText(f"{self.key}{self.pitch}{self.quality}{self.interval}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    w = ChordBuilder()
    w.setStyleSheet("font-size: 24px; font-family: 'Jetbrains Mono'")
    w.show()
    w.submit.connect(print)
    app.exec_()
