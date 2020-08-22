""" Screen for the Guitar Suite that shows the user some stats
    about their progress and lets them enter chords they have learned. """

import chorddata
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication


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
    def __init__(self, *args, **kwargs):
        super(ChordBuilder, self).__init__(*args, **kwargs)
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignCenter)

        self.chord_label = QLabel()
        keys = "A B C D E F G".split()
        pitch = ("\u266E", "\u266F", "\u266D")
        whatarethesecalled = "Maj min dim sus ".split()
        steps = "2 3 4 5 6 7 9 11 13".split()

        for iterable in (keys, pitch, steps, whatarethesecalled):
            row = QWidget()
            hbox = QHBoxLayout(row)
            for char in iterable:
                button = QPushButton(char)
                hbox.addWidget(button)
            self.vbox.addWidget(row)



if __name__ == "__main__":
    app = QApplication([])
    w = ChordBuilder()
    w.setStyleSheet("font-size: 24px; font-family: 'Jetbrains Mono'")
    w.show()
    app.exec_()
