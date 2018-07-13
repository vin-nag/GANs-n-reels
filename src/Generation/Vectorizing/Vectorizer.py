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


def vectorize_frame(df, bar_subdivision=48, reindex=True, pad_bars=True):
    """
    Takes a pandas dataframe and returns it with 2 new frames appended for notes and timing
    bar_subdivision controls how many 'ticks' a bar is split into
    :param df: pandas dataframe with an 'abc' column
    """
    global BAR_SUBDIVISION, NOTE_MULT, PAD_BARS
    BAR_SUBDIVISION = bar_subdivision
    NOTE_MULT = bar_subdivision // 8
    PAD_BARS = pad_bars
    df['notes'], df['timing'] = zip(*df.abc.map(vectorize_abc))
    if reindex: df.reset_index(drop=True, inplace=True)
    return df


def vectorize_abc(abc_string):
    """
    takes an abc string and returns the note vector and timing vector, split by bars
    """
    note_out = []
    time_out = []
    for bar in split_by_bar(abc_string):
        note, time = vectorize_bar(bar)
        note_out.append(note)
        time_out.append(time)
    return np.array(note_out), np.array(time_out)


def split_by_bar(abc_string):
    """
    Takes a string of full ABC notation and splits it into lists representing individual bars
    """
    result = abc_string.split('|')
    return [x for x in result if x != '']


def vectorize_bar(abc_string):
    """
    Takes an ABC string of an individual bar and returns that same bar but with BAR_SUBDIVISION notes
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
            raise Exception(
                "{}*{}/{} is not an integer. Your note multiplier is insufficient".format(NOTE_MULT, num, denom))
            # return np.array(note_out), np.array(time_out)
        reps = ((NOTE_MULT * num) // denom)
        note_num = note_to_number(note)
        note_out += [note_num for n in range(reps)]
        time = [0] * reps
        time[0] = 1
        time_out += time
    # zero padding
    if PAD_BARS and len(note_out) != BAR_SUBDIVISION:
        pad_num = BAR_SUBDIVISION - len(note_out)
        if len(notes) < 4:
            note_out += [0 for n in range(pad_num)]
            time_out += [0 for n in range(pad_num)]
        else:
            note_out = [0 for n in range(pad_num)] + note_out
            note_out = [0 for n in range(pad_num)] + note_out
    return np.array(note_out), np.array(time_out)


def vectorize_bar(abc_string, pad_bars=True):
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
            raise Exception(
                "{}*{}/{} is not an integer. Your note multiplier is insufficient".format(NOTE_MULT, num, denom))
        reps = ((NOTE_MULT * num) // denom)
        note_num = note_to_number(note)
        note_out += [note_num for n in range(reps)]
        time = [0] * reps
        time[0] = 1
        time_out += time
        # zero padding
    if pad_bars and len(note_out) != BAR_SUBDIVISION:
        pad_num = BAR_SUBDIVISION - len(note_out)
        if len(notes) < 4:
            note_out += [0 for n in range(pad_num)]
            time_out += [0 for n in range(pad_num)]
        else:
            note_out = [0 for n in range(pad_num)] + note_out
            note_out = [0 for n in range(pad_num)] + note_out
    return np.array(note_out), np.array(time_out)


# Dicts for note conversion
note_numbers = {
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

accidentals = {'_': -1, '^': 1}
octaves = {',': -12, "'": 12}


def note_to_number(abc_note):
    reg = re.search('([_=^]*)([a-gzA-G])([,\']*)', abc_note)
    accidental = reg.group(1)
    note = reg.group(2)
    octave = reg.group(3)
    val = note_numbers[note]
    if accidental in accidentals:
        val += accidentals[accidental]
    for char in octave:
        val += octaves[char]
    return val
