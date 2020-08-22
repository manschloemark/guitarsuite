"""
    Data structure that keeps track of my guitar practice progress.
    I am revising my old version to make it more pythonic.
"""
import json
import random
import re
import os
import sys
import time

# NOTE: I am wondering if I should make a class or just use a namedtuple

# There are many types of chords this does not account for. I don't think
# I will need to worry about them for the time being.
CHORD_PATTERN = "^[a-gA-G][b#]?[m]?[2345679]?$|^[a-gA-G][b#]?[m]?1[13]$"
chord_regex = re.compile(CHORD_PATTERN)

def parse_chord(chord):
    """
        Takes a string as input and uses regex to verify that it is a valid chord.

        The entire string passed as the argument must be valid - it should not
        output a match if any part of the argument is invalid.
            i.e. passing 'ABCD' should not see 'A' and consider it valid since the pattern
            after it does not match CHORD_PATTERN

        Returns the valid chord with the key capitalized if found and None otherwise.
    """
    chord = chord_regex.search(chord)
    if chord:
        return chord.group(0).capitalize()  # Capitalize the key for consistency
    return None


def normalize_key(chord_a, chord_b):
    """
        Given two chords, make a tuple that is the same form as it would appear
        in a ChordData.scores dict.

        Keys in ChordData.scores are sorted alphabetically.

        Pass each chord through parse_chord to make sure they are proper format
        If either chord returns None, this function will return None
        If both chords return from parse_chord, return a sorted tuple of the two chords
    """
    key = [(parse_chord(chord_a), parse_chord(chord_b))]
    if None in key:
        return None
    return tuple(sorted(key))


class ChordData:
    """
        Class that handles my guitar progress.
        Loads and Saves data about known chords and
        chord changes progress
    """

    def __init__(self, source=None):
        if source != None:
            if os.path.isabs(source):
                self._file = source
            else: # If a filename is given with no path the file is assumed to exist in the same dir as the script
                self._file = os.path.join(os.path.dirname(__file__), source)
        else:
            # Defaults to mychords.txt if no file is given. Maybe there is a way to implement a config that sets the default
            self._file = "./mychords.txt"

        self._load()

    # NOTE should I return copies of the chords and scores? I believe it would be safer because another program could
    #      alter the ChordData.__chords/__scores attributes bypassing the chord parser. But at the same time it is convenient
    #      because the other programs that use the data don't need to worry about updating the objects when adding chords and scores.
    #      At the same time, it kind of defeats the purpose of using a property at all, because it is not any safer.
    @property
    def chords(self):
        """ Returns list containing known chords. No duplicates.
            Returns a copy because the list should be changed using the ChordData.add_chord method"""
        return self.__chords

    @property
    def scores(self):
        """
        Return dict containing all chord pairs playable from known chords and
        high score reached in One-Minute Chord Changes
        """
        return self.__scores

    @property
    def file(self):
        """
            Returns the file that current instance of ChordData is associated with.
        """
        return self._file

    def add_chord(self, chord):
        """
            Add chord to self.chords.
            Chord is first checked by parse_chord to make sure it is a real chord.
            Check if chord is duplicate
            If not duplicate, first update the dict of chord pairs, then add the chord to the list of chords
        """
        chord = parse_chord(chord)

        if chord and chord not in self.chords:
            self._update_chordpairs(chord)
            self.chords.append(chord)
            return True
        return None

    def add_score(self, pair, score, timestamp=None):
        """
        Adds the score the the chord pair's dict of times and scores
        """
        # key = normalize_key(*pair)
        key = pair
        if timestamp == None:
            timestamp = time.time()
        if key in self.scores:
            self.scores[key][timestamp] = score
            return True
        return None

    def _update_chordpairs(self, chord):
        """
            Adds a new key to self.scores for each combination of chord and each
            chord in self.chords

            This function is automatically called when a chord is added to self.chords
            Each new chord pair is initally given a dict with one item: the timestamp of it's creation with a value of None
        """
        for old_chord in self.chords:
            new_key = tuple(sorted([chord, old_chord]))
            self.scores[new_key] = {time.time(): None}

    def random_key(self):
        """
            Uses random.choice to select a key from self.scores
        """
        return random.choice(list(self.scores))

    def weighted_random(self, offset=5):
        """
            Returns a key chosen randomly from self.scores.

            This method is weighted towards keys associated with lower values.
            Use random_key to get a random key with even distribution

            How it is weighted:
                1. Select the target - the lowest score in the dict.
                2. Select a key - use random.choice to pick a key.
                3. Generate an int - use random.randint to pick an int 
                   in range 0 to <key_selected> + offset
                4. if the generated int is less than the target, return that key.
                   else, go back to step 2.

            The parameter offset determines how much to add to the random int each time.
            This makes it so the lowest score is not always guaranteed to be chosen.
            By default the offset is 5.
        """
        keys = list(self.scores)
        target = min(self.scores.values())
        key = random.choice(keys)
        while random.randint(0, self.scores[key] + offset) > target:
            key = random.choice(keys)
        return key

    @file.setter
    def file(self, file):
        self._file = file

    def __enter__(self):
        return self

    def __exit__(self, error_type, value, traceback):
        if traceback is None:
            self._save()
        else:
            raise Exception(error_type, value, traceback)

    def __repr__(self):
        """
            I learned to use self.__class__.__name__ from a talk by Raymond Hittenger.
            This is better than manually typing in the class name because
                A. every class knows it's own name
                B. This is safe in the event of subclassing down the line
        """
        return f"{self.__class__.__name__}('{self._file}')"

    def __str__(self):
        return f"{self.__class__.__name__}(Chords: {len(self.chords)}, Pairs: {len(self.scores)})"

    def _load(self, file=None, sep="&"):
        """
            Loads chords and scores from JSON format txt file If the file does
            not exist it will create it

            The sep parameter sets the character the dictionary keys are using
            to delimit the chords. This is because in Python the dict's keys are
            tuples which do not work with JSON.
        """
        if file is None:
            file = self.file
        try:
            if os.path.getsize(file) == 0:
                self.__chords, self.__scores = [], {}
            else:
                with open(file, "r") as savefile:
                    self.__chords, json_dict = json.load(savefile)
                    # I need to loop through the dict loaded from the file to
                    #   1. Turn the chord pairs into tuples
                    #   2. turn the timestamps into floats.
                    self.__scores = {
                            tuple(key.split(sep)): {float(timestamp): score for timestamp, score in value.items()} for key, value in json_dict.items()
                    }
        except FileNotFoundError:
            # If the given file was not found, don't do anything about it yet because the _save method can create the file.
            self.__chords, self.__scores = [], {}

    def _save(self, file=None, sep="&"):
        """
            Save the contents of self.chords and self.scores to a JSON txt file.
            If no file is given it will save to mychords.txt in the working directory

            The sep parameter sets the character to join the keys of self.scores.
                (Since the keys are tuples which are incompatible with JSON they are
                 converted to strings with <sep>.join(key) )
        """
        if file is None:
            file = self.file
        with open(file, "w+") as savefile:
            json_dict = {sep.join(key): value for key, value in self.scores.items()}
            json.dump([self.chords, json_dict], savefile, indent=2)


# Using properties this way passes a reference to the real chordlist and scoredict. So
# any changes made to the scoredict, even though it is received through the getter,
# changes the Class' property itself.

if __name__ == "__main__":
    if len(sys.argv) > 1:
        c = ChordData(sys.argv[1])
        c.add_chord("A")
        c.add_chord("B")
        print(c.chords)
        c._save()
