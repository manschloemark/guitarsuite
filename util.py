""" module that I will use to store variables that
    should probably be settings in a config file or something.
"""

# Variables so I can just address the score thresholds by a name
bad = 10
poor = 20
okay = 30
decent = 40
good = 50
great = 60
mastery = 100

# Dict containing scores and colors for them
# Chord Pair Buttons will be colored according to the
# highest key they are lower than.
COLOR_DICT = {
        10: "#9d2424", # Bad
        20: "#d0521d", # Poor
        30: "#ea8d00", # Okay
        40: "#e1a500", # Decent
        50: "#94a500", # Good
        60: "#88b03a", # Great
        1000: "#229933" # Mastery
    }
