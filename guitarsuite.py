from chorddata import ChordData
from chordchanges import ChordChanges
from userprogress import UserProgress

import sys

from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QApplication


class GuitarSuite(QWidget):
    """ Main application for the guitar suite program """

    def __init__(self, data, *args, **kwargs):
        super(GuitarSuite, self).__init__(*args, **kwargs)
        self.data = data
        self.vbox = QVBoxLayout(self)

        self.nav = QTabWidget()

        self.chordchanges = ChordChanges(self.data)
        self.userprogress = UserProgress(self.data)

        self.nav.addTab(self.chordchanges, "&Chord Changes")
        self.nav.addTab(self.userprogress, "&My Progress")

        self.nav.currentChanged.connect(self.reload_widget)

        self.vbox.addWidget(self.nav)

    def reload_widget(self, page):
        if page == 0:
            self.chordchanges.refresh()
        elif page == 1:
            self.userprogress.display_stats()


def main(filename):
    with ChordData(filename) as chord_data:
        app = QApplication([])
        gs = GuitarSuite(chord_data)
        with open("guitarsuite_styles.qss") as styles:
            gs.setStyleSheet(styles.read())
        gs.show()
        app.exec_()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(None)

