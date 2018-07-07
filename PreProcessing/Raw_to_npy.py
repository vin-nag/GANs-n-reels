from PreProcessing import Generate_Files
import os

#

# Flag for whether to update the Tunes_raw.py file from the session's github.
# If true, the raw data will update, if false, the data won't update.
UPDATE_RAW = False

# The file to write to.
# Note* Writes the data to '.py' and the statistics to '_stats.txt' automatically.
FOLDER_NAME = '../Tunes'
FILE_NAME = 'Common_Time'
if FOLDER_NAME not in os.listdir(os.getcwd()):
    try:  os.mkdir(FOLDER_NAME)
    except FileExistsError: pass
tunes = Generate_Files.raw_to_dict(FILE_NAME, default_folder=FOLDER_NAME, update=UPDATE_RAW,
                                   types=[],
                                   meters=['4/4'],
                                   modes=[])

# tunes is now the cleaned dictionary, you can continue the stremalined processing from here.


if __name__ == '__main__':
    pass



