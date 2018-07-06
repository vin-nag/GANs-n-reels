notes_to_num = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
         'E': 4, 'Fb': 4, 'E#': 5, 'F': 5, 'F#': 6, 'Gb': 6,
         'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10,
         'B': 11, 'Cb': 11, 'B#': 0}


num_to_notes = {0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F',
                6: 'F#', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}

key_list = ['Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#']


modes = {'Ionian': 0, 'Major': 0, 'Dorian': 2, 'Phrygian': 4, 'Lydian': 5,
         'Mixolydian': 7, 'Aeolian': 9, 'Minor': 9, 'Locrian': 11}

sharp_order = 'FCGDAEB'
flat_order = 'BEADGCF'

# 12 semi-tones per octave
# Up a key: +7 or -5
# Down a key: -7 or +5

# key_list index - 5 = number of accidentals, where + is sharps and - is flats.

