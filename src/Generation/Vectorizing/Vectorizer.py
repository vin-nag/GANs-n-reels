"""
Vectorizer converts cleaned ABC notation into explicit subdivisions of time
"""

import numpy as np
import pandas as pd
import re

# Constants
BAR_SUBDIVISION = 48
NOTE_MULT = BAR_SUBDIVISION // 8  # value to multiply an 8th note by
PAD_BARS = True
PAD_METHOD = 1  # 1 is stretch

# region MUSIC THEORY STRUCTS
# Dicts for note conversion
chars_as_num = {
    'C': 60,
    'D': 62,
    'E': 64,
    'F': 65,
    'G': 67,
    'A': 69,
    'B': 71,
    'c': 72,
    'd': 74,
    'e': 76,
    'f': 77,
    'g': 79,
    'a': 81,
    'b': 83,
    'z': 0
}

accidental_mods = {'_': -1, '=': 0, '^': 1}
octave_mods = {',': -12, "'": 12}


key_to_offset = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
                'E': 4, 'Fb': 4, 'E#': 5, 'F': 5, 'F#': 6, 'Gb': 6,
                'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10,
                'B': 11, 'Cb': 11, 'B#': 0}


offset_to_key = {0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F',
                 6: 'F#', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}

ordered_key_list = ['Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#']


modes = {'ionian': 0, 'major': 0, 'dorian': 2, 'phrygian': 4, 'lydian': 5,
         'mixolydian': 7, 'aeolian': 9, 'minor': 9, 'locrian': 11}

sharp_order = 'FCGDAEB'
flat_order = 'BEADGCF'

# 12 semi-tones per octave
# Up a key: +7 or -5
# Down a key: -7 or +5

# key_list index - 5 = number of accidentals, where + is sharps and - is flats.
# endregion


def vectorize_frame(df, bar_subdivision=48, reindex=True, pad_bars=True):
    """
    Takes a pandas dataframe and returns it with 2 new columns appended for notes and timing
    bar_subdivision controls how many 'ticks' a bar is split into
    :param df: pandas dataframe with an 'abc' column
    """
    global BAR_SUBDIVISION, NOTE_MULT, PAD_BARS
    BAR_SUBDIVISION = bar_subdivision
    NOTE_MULT = bar_subdivision // 8
    PAD_BARS = pad_bars
    df['notes'], df['timing'] = zip(*df.apply(vectorize_abc, axis=1))
    # TODO - Multiply the spots with 0's by 0, and everything else by 1
    df['notes'] = (df['notes'] + df['mode'].map(transpose_tune))
    if reindex: df.reset_index(drop=True, inplace=True)
    return df


def vectorize_abc(df):
    """
    takes an abc string and returns the note vector and timing vector, split by bars
    """

    abc_string = df['abc']
    accs, mod = get_sharps_or_flats(df['mode'])
    note_out = []
    time_out = []
    for bar in split_by_bar(abc_string):
        note, time = vectorize_bar(bar, accs, mod)
        note_out.append(note)
        time_out.append(time)
    return np.array(note_out), np.array(time_out)


def split_by_bar(abc_string):
    """
    Takes a string of full ABC notation and splits it into lists representing individual bars
    """
    result = abc_string.split('|')
    return [x for x in result if x != '']


def vectorize_bar(abc_string, accs, mod, pad_bars=True):
    """
    Takes an ABC string of an individual bar and returns that same bar but with 48 notes
    returns the the string of notes as well as a 'timing vector'
    """
    note_out = []
    time_out = []
    notes_re = re.compile('([_=^]*[a-gzA-G][,\']*)([\d]*)/?([\d]*)')
    notes = notes_re.findall(abc_string)
    for note, num, denom in notes:
        if num == '':
            num = 1
        else:
            num = int(num)
        if denom == '':
            denom = 1
        else:
            denom = int(denom)
        if NOTE_MULT * num / denom % 1 != 0:
            return np.array(note_out), np.array(time_out)
        reps = ((NOTE_MULT * num) // denom)
        note_num = note_to_number(note, accs, mod)
        note_out += [note_num for _ in range(reps)]
        time = [0] * reps
        time[0] = 1
        time_out += time
        # zero padding
    if pad_bars and len(note_out) != BAR_SUBDIVISION:
        pad_num = BAR_SUBDIVISION - len(note_out)
        if len(notes) < 4:
            note_out += [0 for _ in range(pad_num)]
            time_out += [0 for _ in range(pad_num)]
        else:
            note_out = [0 for _ in range(pad_num)] + note_out
            time_out = [0 for _ in range(pad_num)] + time_out
    return np.array(note_out), np.array(time_out)


def get_sharps_or_flats(key):
    # TODO - Fix the fact that sharp or flat keys will be missed.

    tonic = key_to_offset[key[0]]
    mode = modes[key[1:]]
    relative = offset_to_key[(tonic - mode) % 12]

    diff = ordered_key_list.index(relative) - 5

    if diff > 0:
        return sharp_order[0:diff-1], 1
    elif diff < 0:
        return flat_order[0:diff-1], -1
    else:
        return '', 0


def transpose_tune(key):
    tonic = key_to_offset[key[0]]
    mode = modes[key[1:]]
    relative = offset_to_key[(tonic - mode) % 12]

    diff = ordered_key_list.index(relative) - 5

    trans_up = (7 * diff) % 12
    trans_down = (5 * diff % 12)

    if trans_up < trans_down:
        return trans_up
    else:
        return -trans_down


def note_to_number(abc_note, accs, mod):
    reg = re.search('([_=^]*)([a-gzA-G])([,\']*)', abc_note)
    accidental = reg.group(1)
    note = reg.group(2)
    octave = reg.group(3)
    val = chars_as_num[note]
    if accidental != '':
        for char in accidental:
            val += accidental_mods[char]
    else:
        if note.upper() in accs:
            val += mod
    for char in octave:
        val += octave_mods[char]
    return val


if __name__ == '__main__':
    from Data.Clean.Common_Time import tunes as tunes_raw
    print('Creating dataframe...')
    tunes = pd.DataFrame.from_dict(tunes_raw, orient='index')
    tunes['abc_raw'] = tunes.abc # preserve the original abc strings
    tunes = vectorize_frame(tunes, pad_bars=True)


