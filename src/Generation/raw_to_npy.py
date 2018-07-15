from Data.Raw import The_Session_Raw as raw
from src.Generation.Cleaning import Generate_Stats, Generate_Files
from src.Generation.Vectorizing import Vectorizer
import os
import pandas as pd
import numpy as np


# Flag for whether to update the Tunes_raw.py file from the session's github.
# If true, the Raw Data will update, if false, the Data won't update.
UPDATE_RAW = False

# The files to write to.
FOLDER_NAME = '../../Data'
ABC_OUT = '/Clean/'
STATS_OUT = '/Statistics/'
NPY_OUT = '/Vectors/'
FILE_NAME = 'Common_Time'

#
TYPES = []
METER = ['4/4']
MODES = []

BAR_SUBDIVISION = 48


def make_folder(f_name):
    if f_name not in os.listdir(os.getcwd()):
        try:
            os.mkdir(f_name)
            print('Created folder "{}"'.format(f_name))
        except FileExistsError:
            print('Folder "{}" already exists. Skipping creation...'.format(f_name))


def raw_to_dict(types=None, meters=None, modes=None, update=False):
    """
    :param types: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param meters: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param modes: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param update: Flag to update the Raw Data from the Session's Github page.
    :return:
    """

    # If the update flag is set, retrieve the new Data from the Session.
    if update: Generate_Files.update_tunes()

    # Sort the tunes and hand it to the cleaning function.
    clean = Generate_Files.create_dict_list(raw.tunes, types=types, meters=meters, modes=modes)

    # Generate the stats of the cleaned tunes and save them. Has a small check to prevent a file-out error.
    Generate_Stats.parse_stats(clean, FOLDER_NAME + STATS_OUT + FILE_NAME + '.txt')
    Generate_Files.dicts_to_file(clean, FOLDER_NAME + ABC_OUT + FILE_NAME + '.py')

    tunes = dict()
    for x in clean: tunes[x['setting']] = x
    return tunes


def raw_abc_to_npy_file():
    make_folder(FOLDER_NAME)
    make_folder(FOLDER_NAME + ABC_OUT)
    make_folder(FOLDER_NAME + STATS_OUT)
    make_folder(FOLDER_NAME + NPY_OUT)

    print('Starting abc cleaning...')
    # TODO - Using the dictionary provided by the raw_to_dict function causes the numpy array to throw an error.
    tunes = raw_to_dict(update=UPDATE_RAW, types=[], meters=['4/4'], modes=[])

    print('Finished cleaning abc strings.')
    print('Starting vectorization process.')
    from Data.Clean.Common_Time import tunes as tunes_raw
    print('Creating dataframe...')
    tunes = pd.DataFrame.from_dict(tunes_raw, orient='index')
    tunes['abc_raw'] = tunes.abc # preserve the original abc strings
    tunes = Vectorizer.vectorize_frame(tunes, pad_bars=True, bar_subdivision=16)

    print("Size of Initial Frame: {}".format(len(tunes.index)))
    tunes.head()
    tunes_shaped = tunes[[len(tune.shape)==2 for tune in tunes.notes]].copy()
    print("Size of Cleaned Frame: {}".format(len(tunes_shaped.index)))
    tunes_shaped.reset_index(drop=True, inplace=True)
    print('\n - - - - - - - Table Data - - - - - - - \n')
    print(tunes_shaped.head()['notes'])
    for x in tunes_shaped.head()['notes']:
        print('Tune')
        for y in x: print(y)
        print()

    np.save(FOLDER_NAME + NPY_OUT + FILE_NAME + '_Notes.npy', tunes_shaped.notes.values)
    np.save(FOLDER_NAME + NPY_OUT + FILE_NAME + '_Time.npy', tunes_shaped.timing.values)


if __name__ == '__main__':
    raw_abc_to_npy_file()