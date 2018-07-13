from src.Generation import Generate_Files
import os
import pandas as pd
import numpy as np
import src.Generation.Vectorizer as Vectorizer

# Flag for whether to update the Tunes_raw.py file from the session's github.
# If true, the raw Data will update, if false, the Data won't update.
UPDATE_RAW = False

# The files to write to.
FOLDER_NAME = '../Tunes'
PYTHON_FILE_NAME = 'Common_Time'
NUMPY_FILE_NAME = 'tunes'

BAR_SUBDIVISION = 48


def make_folder(f_name):
    if f_name not in os.listdir(os.getcwd()):
        try:
            os.mkdir(f_name)
            print('Created folder "{}"'.format(f_name))
        except FileExistsError:
            print('Folder "{}" already exists. Skipping creation...'.format(f_name))


def raw_abc_to_npy_file():
    make_folder(FOLDER_NAME)
    make_folder(FOLDER_NAME + '/abc')
    make_folder(FOLDER_NAME + '/npy')

    print('Starting abc cleaning...')
    # TODO - Using the dictionary provided by the raw_to_dict function causes the numpy array to throw an error.
    tunes = Generate_Files.raw_to_dict(PYTHON_FILE_NAME, default_folder=FOLDER_NAME + '/abc', update=UPDATE_RAW,
                                       types=[],
                                       meters=['4/4'],
                                       modes=[])

    print('Finished cleaning abc strings.')
    print('Starting vectorization process.')
    from Tunes.abc.Common_Time import tunes as tunes_raw
    print('Creating dataframe...')
    tunes = pd.DataFrame.from_dict(tunes_raw, orient='index')
    tunes['abc_raw'] = tunes.abc # preserve the original abc strings
    tunes = Vectorizer.vectorize_frame(tunes, pad_bars=True)

    print("Size of Initial Frame: {}".format(len(tunes.index)))
    tunes.head()
    tunes_shaped = tunes[[len(tune.shape)==2 for tune in tunes.notes]].copy()
    print("Size of Cleaned Frame: {}".format(len(tunes_shaped.index)))
    tunes_shaped.reset_index(drop=True, inplace=True)
    tunes_shaped.head()

    np.save(FOLDER_NAME + '/npy/' + NUMPY_FILE_NAME + '_notes', tunes_shaped.notes.values)
    np.save(FOLDER_NAME + '/npy/' + NUMPY_FILE_NAME + '_time', tunes_shaped.timing.values)


if __name__ == '__main__':
    raw_abc_to_npy_file()