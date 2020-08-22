""" CLI program that lets you add chords you've learned to your file """
from chorddata import ChordData
import os
import sys

if len(sys.argv) > 1:
    with ChordData(sys.argv[1]) as cd:
        passed = []
        failed = []

        for chord in sys.argv[2:]:
            if cd.add_chord(chord):
                passed.append(chord)
            else:
                failed.append(chord)
    print("Added", passed)
    print("Could not add", failed)
