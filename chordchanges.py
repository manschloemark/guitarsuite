""" Graphical User Interface to facilitate 60 second chord changes """
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QBasicTimer
from PyQt5.QtWidgets import (
    QSizePolicy,
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QLCDNumber,
)
from PyQt5.QtGui import QColor, QFont, QPalette
import chorddata
import util
import time


class ChordChanges(QWidget):
    """
       Facilitates 60 second chord changes
       Pick a pair of chord changes and play them
       alternating for one minute. Enter the number of times
       you played each chord combined to submit your score.
    """

    def __init__(self, data, *args, **kwargs):
        super(ChordChanges, self).__init__(*args, **kwargs)
        self.setWindowTitle("60 Second Chord Changes")
        self.setProperty("id", "main")
        self.data = data
        self.__key = None

        #self.hbox = QHBoxLayout(self)

        #self.control_container = QWidget()
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.setSpacing(4)

        self.scoreboard = Scoreboard()
        self.scoreboard.setProperty("id", "scoreboard")
        self.vbox.addWidget(self.scoreboard)

        self.start_button = QPushButton("Start Timer")
        self.start_button.setEnabled(False)
        self.start_button.setProperty("id", "start")
        self.start_button.clicked.connect(self.start_session)
        self.vbox.addWidget(self.start_button)
        self.vbox.setAlignment(self.start_button, Qt.AlignCenter)

        self.cancel = QPushButton("Cancel")
        self.cancel.setEnabled(False)
        self.cancel.setProperty("id", "cancel")
        self.cancel.clicked.connect(self.cancel_session)
        self.vbox.addWidget(self.cancel)
        self.vbox.setAlignment(self.cancel, Qt.AlignCenter)

        self.content = QWidget()
        self.content.setProperty("id", "content")
        self.vbox.addWidget(self.content)
        self.content_stack = QStackedLayout(self.content)

        # Subwidgets of self.content -- Chord Selection, Timer, Score Input

        self.chord_select = ChordSelect(data)
        self.chord_select.setProperty("id", "chord_select")
        self.content_stack.addWidget(self.chord_select)
        self.chord_select.pair_selected.connect(self.set_key)

        self.timer = PlayTimer()
        self.timer.done.connect(self.session_finished)
        self.content_stack.addWidget(self.timer)

        self.score_input = ScoreInput()
        self.content_stack.addWidget(self.score_input)
        self.score_input.submit.connect(self.enter_score)

        self.results = Results()
        self.content_stack.addWidget(self.results)
        self.results.ok.clicked.connect(self.raise_chordselect)


        with open("chordchange_styles.qss") as styles:
            self.setStyleSheet(styles.read())

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, key):
        self.__key = key

    def set_key(self, key, score):
        self.start_button.setEnabled(True)
        self.key = key
        self.scoreboard.update_key(key, score)

    def start_session(self):
        if self.key:
            self.content_stack.setCurrentWidget(self.timer)
            self.cancel.setEnabled(True)
            self.timer.start_timer()

    def cancel_session(self):
        self.content_stack.setCurrentWidget(self.chord_select)
        self.timer.clock.stop()
        self.cancel.setEnabled(False)

    def session_finished(self):
        self.content_stack.setCurrentWidget(self.score_input)

    def enter_score(self, score):
        old_score = self.data.highscore(self.key)
        self.data.add_score(self.key, score, time.time())
        if score > old_score:
            self.chord_select.chord_pair_grid.button_dict[self.key].score = score
            self.scoreboard.update_score(score)
            self.results.generate_results(True, old_score, score)
        else:
            self.results.generate_results(False, old_score, score)
        self.content_stack.setCurrentWidget(self.results)

    def raise_chordselect(self):
        self.cancel.setEnabled(False)
        self.content_stack.setCurrentWidget(self.chord_select)

    def refresh(self):
        self.raise_chordselect()
        self.chord_select.refresh()


class Scoreboard(QWidget):
    """ Simple widget used to display currently selected chord pair
        and high score for it """

    def __init__(self, *args, **kwargs):
        super(Scoreboard, self).__init__(*args, **kwargs)
        self.vbox = QVBoxLayout(self)

        self.chordlabel = QLabel("" * 13)
        self.chordlabel.setProperty("id", "chordlabel")
        #self.chordlabel.setFixedHeight()
        self.vbox.addWidget(self.chordlabel)
        self.high_score = QLabel("Select a chord pair!")
        self.high_score.setProperty("id", "scorelabel")
        #self.high_score.setFixedHeight(8)
        self.vbox.addWidget(self.high_score)

        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.setAlignment(self.high_score, Qt.AlignCenter)

    def update_key(self, chord_pair, score):
        self.chordlabel.setText(f"{chord_pair[0]:<5} & {chord_pair[1]:>5}")
        self.update_score(score)

    def update_score(self, score):
        self.high_score.setText(f"High Score:  {score:>3}")


# Main Content Widgets
class ChordSelect(QWidget):
    """ Widget that contains all controls for selecting chord pair """

    pair_selected = pyqtSignal(tuple, int)

    def __init__(self, data, *args, **kwargs):
        super(ChordSelect, self).__init__(*args, **kwargs)
        self.data = data
        self.vbox = QVBoxLayout(self)
        self.randoms_container = QWidget()
        self.randoms_hbox = QHBoxLayout(self.randoms_container)

        self.random = QPushButton("Random Pair")
        self.random.setToolTip("All pairs are equally likely")
        self.random.clicked.connect(self.emit_random)
        self.weighted = QPushButton("Weighted Random")
        self.weighted.setToolTip("Lower scores are more likely")
        self.weighted.clicked.connect(self.emit_weighted)

        self.randoms_hbox.addWidget(self.weighted)
        self.randoms_hbox.addWidget(self.random)

        self.chord_pair_grid = ChordPairGrid(data)
        self.chord_pair_grid.pair_clicked.connect(self.pair_selected)

        self.vbox.addWidget(self.randoms_container)
        self.vbox.addWidget(self.chord_pair_grid)

    def emit_random(self, x):
        """ Calls a chorddata object's random_key method and passes
            the result through the pair_selected signal
            The parameter x is a throwaway value from the PushButton.clicked signal """
        key = self.data.random_key()
        self.pair_selected.emit(key, self.data.highscore(key))

    def emit_weighted(self, x):
        """ Calls a chorddata object's random_key method and passes
            the result through the pair_selected signal
            The parameter x is a throwaway value from the PushButton.clicked signal """
        key = self.data.weighted_random()
        self.pair_selected.emit(key, self.data.highscore(key))

    def refresh(self):
        self.chord_pair_grid.make_buttons()
        self.chord_pair_grid.rearrange()


class ChordPairGrid(QWidget):
    """ Widget that contains a grid of buttons for each key in
        the chord pair dictionary, and controls to rearrange them """

    pair_clicked = pyqtSignal(tuple, int)

    def __init__(self, data, *args, **kwargs):
        super(ChordPairGrid, self).__init__(*args, **kwargs)
        self.data = data
        self.button_size = (96, 36)
        self.column_spacing = 8

        self.layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.grid_container = QWidget()
        self.grid_container.setProperty('id', 'gridcontainer')
        self.pair_grid = QGridLayout(self.grid_container)
        self.pair_grid.setSpacing(self.column_spacing)

        self.scroll_area.setWidget(self.grid_container)
        self.scroll_area.ensureWidgetVisible(self)

        # Controls to rearrange the grid
        sort_controls = QWidget()
        self.sort_layout = QHBoxLayout(sort_controls)
        sort_label = QLabel("Sort")
        # For some reason using the toggle sinal for the radiobuttons and checkbox makes the
        # sort_buttons method execute twice. The clicked signal does not... huh.
        self.sort_alphabetically = QRadioButton("by Chords")
        self.sort_alphabetically.clicked.connect(self.rearrange)
        self.sort_numerically = QRadioButton("by Score")
        self.sort_numerically.clicked.connect(self.rearrange)
        self.reverse = QCheckBox("Reverse")
        self.reverse.clicked.connect(self.rearrange)

        self.sort_layout.addWidget(sort_label)
        self.sort_layout.addWidget(self.sort_alphabetically)
        self.sort_layout.addWidget(self.sort_numerically)
        self.sort_layout.addWidget(self.reverse)

        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(sort_controls)
        self.init_grid()

    def init_grid(self):
        self.make_buttons()
        self.rearrange()

    def make_buttons(self):
        self.button_dict = {}
        self.buttons = []  # This is used to make it easy to sort the buttons

        for pair in self.data.scores:
            score = self.data.highscore(pair)
            if pair not in self.button_dict:
                new_button = PairButton(pair, score, self.button_size)
                new_button.clicked.connect(self.pair_clicked.emit)
                self.button_dict[pair] = new_button
                self.buttons.append(new_button)

    def sort_buttons(self):
        rev = self.reverse.isChecked()
        if self.sort_alphabetically.isChecked():
            self.buttons = sorted(
                self.button_dict.values(), reverse=rev, key=lambda button: button.pair
            )
        elif self.sort_numerically.isChecked():
            self.buttons = sorted(
                self.button_dict.values(), reverse=rev, key=lambda button: button.score
            )

    def set_grid(self):
        # Calculate num_cols based on width of container
        # As far as I am aware there is no way to get the actual width
        # of the scroll bar. So I am estimating...
        scrollbar_width = 20
        row_length = self.scroll_area.width() - self.column_spacing - scrollbar_width
        button_space = self.button_size[0] + self.column_spacing
        num_cols = row_length // button_space
        for count, button in enumerate(self.buttons):
            row = count // num_cols
            col = count % num_cols
            self.pair_grid.addWidget(button, row, col)

    def new_pairs(self):
        self.make_buttons()
        self.rearrange()

    def clear_grid(self):
        for i in reversed(range(self.pair_grid.count())):
            self.pair_grid.itemAt(i).widget().setParent(None)

    def rearrange(self):
        self.clear_grid()
        self.sort_buttons()
        self.set_grid()

    def resizeEvent(self, e):
        self.rearrange()


class PairButton(QPushButton):
    """ Subclass of pushbutton to encapsulate assignment of chord
        pair data and styles to buttons in the chord pair grid """
    clicked = pyqtSignal(tuple, int)

    def __init__(self, pair, score, size, *args, **kwargs):
        super(PairButton, self).__init__(*args, **kwargs)
        self.pair = pair
        self.score = score
        self.setText("+".join(pair))
        self.setFixedSize(*size)
        self.setProperty("type", "pairbutton")
        self.clicked.__delattr__

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, score):
        self.__score = score
        self.set_color()

    def set_color(self):
        """
            Sets the color based on the COLOR_DICT
        """
        for threshold in util.COLOR_DICT:
            if self.score <= threshold:
                self.setStyleSheet(f"background-color: {util.COLOR_DICT[threshold]};")
                return

    def mousePressEvent(self, e):
        self.clicked.emit(self.pair, self.score)

class PlayTimer(QWidget):
    done = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setProperty('id', 'timer')
        vbox = QVBoxLayout(self)

        self.instructions = QLabel(self)
        self.instructions.setProperty("id", "timer-instruction")
        self.lcd = QLCDNumber(2, self)
        self.clock = QBasicTimer()

        vbox.addWidget(self.instructions)
        vbox.addWidget(self.lcd)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setAlignment(self.instructions, Qt.AlignCenter)

    def timerEvent(self, e):
        if self.preptime > 1:
            self.preptime -= 1
            self.lcd.display(self.preptime)
        elif self.runtime == 60:
            self.lcd.display(self.runtime)
            self.runtime -= 1
            self.instructions.setText("Play!")
        elif self.runtime > 0:
            self.lcd.display(self.runtime)
            self.runtime -= 1
        else:
            self.clock.stop()
            self.done.emit()

    def resizeEvent(self, e):
        self.lcd.setFixedSize(e.size().width() // 2, e.size().height() // 2)

    def start_timer(self):
        self.preptime, self.runtime = 3, 60
        self.instructions.setText("Get ready!")
        self.lcd.display(self.preptime)
        self.clock.start(1000, self)

#class PlayTimer(QWidget):
#    """ Widget that displays a short timer and then a full 60 second timer """
#
#    done = pyqtSignal()
#    _preptime = 3
#    _runtime = 60
#
#    def __init__(self, *args, **kwargs):
#        super(PlayTimer, self).__init__(*args, **kwargs)
#        self.setProperty("id", "timer")
#        self.vbox = QVBoxLayout(self)
#        self.vbox.setAlignment(Qt.AlignCenter)
#        self.vbox.setSpacing(8)
#        self.instruction = QLabel()
#        self.instruction.setProperty("id", "timer-instruction")
#        self.vbox.addWidget(self.instruction)
#        self.lcd = QLCDNumber()
#        self.lcd.setProperty("id", "timer-display")
#        self.vbox.addWidget(self.lcd)
#        self.vbox.setAlignment(self.lcd, Qt.AlignCenter)
#        self.clock = QBasicTimer()
#        self.reset()
#
#    def timerEvent(self, e):
#        if self.preptime > 0:
#            self.lcd.display(self.preptime)
#            self.preptime -= 1
#        elif self.runtime > 0:
#            if self.runtime == 60:
#                self.instruction.setText("Play!")
#            self.lcd.display(self.runtime)
#            self.runtime -= 1
#        else:
#            self.clock.stop()
#            self.done.emit()
#
#    def start(self):
#        self.reset()
#        self.clock.start(1000, self)
#
#    def reset(self):
#        """ Preptime is 3 seconds long but the variable is 2 because
#            the first second happens when the timer is started.
#            Runtime is 60 seconds """
#        self.clock.stop()
#        self.preptime = self._preptime
#        self.runtime =  self._runtime
#        self.instruction.setText("Get ready!")
#
#    def tick(self):
#        if self.preptime != 0:
#            self.display.setText(str(self.preptime))
#            self.preptime -= 1
#        elif self.runtime != 0:
#            if self.runtime == self._runtime:
#                self.instruction.setText("Start!")
#            self.display.setText(str(self.runtime))
#            self.runtime -= 1
#        else:
#            self.clock.stop()
#            self.done.emit()


class ScoreInput(QWidget):
    """ Widget that lets user enter number of times they played their
        chord pair. Sends that number to the chorddata object """

    submit = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(ScoreInput, self).__init__(*args, **kwargs)
        self.vbox = QVBoxLayout(self)

        self.instruction = QLabel("How many times did you play the chords?")
        self.instruction.setProperty("id", "input-instruction")
        self.vbox.addWidget(self.instruction)
        self.vbox.setAlignment(Qt.AlignCenter)
        input_container = QWidget()
        self.input_hbox = QHBoxLayout(input_container)
        self.input_hbox.setAlignment(Qt.AlignCenter)
        self.user_input = QSpinBox()
        self.user_input.setRange(0, 999)
        self.input_hbox.addWidget(self.user_input)
        self.submit_button = QPushButton("Submit")
        self.submit_button.setProperty("id", "score-input")
        self.input_hbox.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.submit_score)

        self.vbox.addWidget(input_container)

    def submit_score(self):
        score = self.user_input.value()
        self.submit.emit(score)
        self.user_input.clear()


class Results(QWidget):
    """
        Shows the results for the session that just finished
        Tells whether the score entered is greater than the previous score
    """

    def __init__(self, *args, **kwargs):
        super(Results, self).__init__(*args, **kwargs)
        self.setProperty("id", "results")
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.setSpacing(4)
        self.message = QLabel()
        self.message.setProperty("id", "result")
        self.vbox.setAlignment(self.message, Qt.AlignCenter)
        self.vbox.addWidget(self.message)
        self.old_high_score = QLabel()
        self.old_high_score.setProperty("type", "results-label")
        self.vbox.addWidget(self.old_high_score)
        self.vbox.setAlignment(self.old_high_score, Qt.AlignCenter)
        self.score_entered = QLabel()
        self.score_entered.setProperty("type", "results-label")
        self.vbox.addWidget(self.score_entered)
        self.vbox.setAlignment(self.score_entered, Qt.AlignCenter)
        self.ok = QPushButton("OK")
        self.vbox.addWidget(self.ok)

    def generate_results(self, passed, old, new):
        if passed:
            self.message.setText("New high score!")
            self.old_high_score.setText(f"Old High Score:{old:>8}")
            self.score_entered.setText(f"New High Score:{new:>8}")
            self.message.setStyleSheet("color: green")
            self.old_high_score.setStyleSheet("color: red")
            self.score_entered.setStyleSheet("color: green")
        else:
            self.message.setText("You did not beat your score...")
            self.old_high_score.setText(f"Old High Score:{old:>8}")
            self.score_entered.setText(f"Your attempt:{new:>10}")
            self.message.setStyleSheet("color: red")
            self.old_high_score.setStyleSheet("color: white")
            self.score_entered.setStyleSheet("color: red")


def main():
    # Testing
    # TODO: clean this up
    import sys

    test_data = chorddata.ChordData(sys.argv[1])
    a = QApplication([])
    b = ChordChanges(test_data)
    with open("guitarsuite_styles.qss") as styles:
        b.setStyleSheet(styles.read())
    if 't' in sys.argv[1]:
        b.timer._preptime = 1
        b.timer._runtime = 1
    b.show()
    a.exec_()

    test_data._save()


if __name__ == "__main__":
    main()
