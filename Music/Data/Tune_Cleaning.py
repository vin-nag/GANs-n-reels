"""
Module for modifying the tunes dataset
There are 4 stages to prepping the data: Conversion, Filtering, Cleaning, Vectorizing

Conversion:
    Conversion is the process of converting abc notation into a python readable format. This is performed outside of this module
Filtering:
    Filtering is the process of removing entries from the dataset entirely that are deemed unsuitable as training data
Cleaning:
    Cleaning is the process of removing or modifying elements of the abc string itself
Vectorizing:
    Vectorizing is the process of converting filtered and cleaned strings into matricies of numbers

Note that throughout this module "filtering" means removing rows entirely while "cleaning" means modifying them inplace
"""
from Tunes_cleaned import tunes
import pandas as pd

tunes_frame_raw = pd.DataFrame.from_dict(tunes, orient='index')


def get_tunes_clean():
    return clean_tunes(filter_tunes())


# region FILTERING

def filter_tunes(tunes=tunes_frame_raw, common_time=True, tuplets=True, non_diatonic=True, small_strings=True,
                 min_str_len=32):
    """
    Applies several filtering methods to a dataframe of abc notation, removing incompatible rows
    :param tunes: Pandas dataframe constructed from an ABC notation dictionary
    :return: tunes with all selected filtering applied
    """
    if common_time: tunes = filter_common_time(tunes)
    if tuplets: tunes = filter_tuplets(tunes)
    if non_diatonic: tunes = filter_non_diatonic(tunes)
    if small_strings: tunes = filter_small_strings(tunes, min_str_len)
    return tunes


def filter_common_time(frame):
    """
    takes a tunes dict and removes all entries whose meter != 4/4
    """
    return frame.drop(frame[frame['meter'] != '4/4'].index)


def filter_tuplets(frame):
    """
    Tuplets are occurrences of irrational time
    """
    return frame.drop(frame[frame['abc'].str.count('\(\d') > 0].index)


def filter_non_diatonic(frame):
    """
    Non-diatonic notes are notes not found within the default key signature
    """
    return frame.drop(frame[frame['abc'].str.count('\^|_|=') > 0].index)


def filter_small_strings(frame, len=32):
    """
    Removes all rows with abc strings below a certain length
    """
    return frame.drop(frame[frame.abc.str.len() < len].index)


# endregion

# region CLEANING

def clean_tunes(tunes, remarks=True, ornamentation=True, quotations=True, barlines=True, gracenotes=True, slurs=True):
    if remarks: tunes = clean_remarks(tunes)
    if ornamentation: tunes = clean_ornamentation(tunes)
    if quotations: tunes = clean_quotations(tunes)
    if barlines: tunes = clean_barlines(tunes)
    if gracenotes: tunes = clean_gracenotes(tunes)
    if slurs: tunes = clean_slurs(tunes)
    return tunes


def clean_remarks(frame):
    """
    Remarks are extraneous information contained in square brackets
    """
    frame['abc'] = frame['abc'].str.replace('\[.*?\]', '')
    return frame


def clean_ornamentation(frame):
    """
    Ornamentation represents trills or other performance enhancers
    See http://abcnotation.com/wiki/abc:standard:v2.1#decorations
    .       staccato mark
    ~       Irish roll
    H       fermata
    L       accent or emphasis
    M       lowermordent
    O       coda
    P       uppermordent
    S       segno
    T       trill
    u       up-bow
    v       down-bow
    """
    frame['abc'] = frame['abc'].str.replace("[\.~HLMOPSTuv]", '')
    return frame


def clean_quotations(frame):
    """
    Chord symbols are typically placed within quotation marks
    """
    frame['abc'] = frame['abc'].str.replace('".*?"', '')
    return frame


def clean_barlines(frame):
    """
    Turns all barlines and repeatlines into single '|' characters
    see http://abcnotation.com/wiki/abc:standard:v2.1#repeat_bar_symbols
    """
    frame['abc'] = frame['abc'].str.replace('\|:|:\||\|\]|\[\||::', '|')
    frame['abc'] = frame['abc'].str.replace('\|+', '|')
    return frame

def clean_gracenotes(frame):
    """
    Gracenotes are ornamental notes that are meant to be played so quickly as to not take any time
    They are denoted by placing notes in braces
    """
    frame['abc'] = frame['abc'].str.replace('{.*?}', '')
    return frame

def clean_slurs(frame):
    """
    slurs indicate that notes should be played with minimal separation, in a legato style
    They are denoted by placing notes in parentheses
    """
    frame['abc'] = frame['abc'].str.replace('(.*?)', '')
    return frame

# endregion

# region Vectorizing

# === NOTE CONVERSION ==
# The goal of note conversion is to turn strings of characters into numeric vectors

def vectorize_tunes(frame):
    """
    given a frame with an 'abc' column, it creates two new columns, 'abc_unfolded', 'hold_vector' and 'abc_vectorized'
    abc_unfolded is abc notation but with timing data made explicit (each note representing a 16th note)
    hold_vector is a vector where 0s represent distinct notes and 1s represent a continued note from the previous step
    abc_vectorized is the same as abc_unfolded but with the letters converted into numbers
    """
    pass

def unfold_abc():
    """
    given an abc list returns a tuple of 2 lists: notes and holds
    """
    pass

def unfold_bar():
    """
    given a bar of abc notation it expands each note to represent timing information explicitly
    """
    pass




# Dictionary to help convert ABC to numbers, 60 represents middle c as in the MIDI standard
notes = {
    'C': 60,
    'D': 61,
    'E': 62,
    'F': 63,
    'G': 64,
    'A': 65,
    'B': 66,
    'c': 67,
    'd': 68,
    'e': 69,
    'f': 70,
    'g': 71,
    'a': 72,
    'b': 73
}

transpose = {
    'C': 0,
    'D': -2,
    'E': -4,
    'F': -5,
    'G': -7,
    'A': -9,
    'B': -11,
}

# endregion

if __name__ == '__main__':
    print(get_tunes_clean().head)