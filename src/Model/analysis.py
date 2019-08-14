import tensorflow as tf
import numpy as np
from scipy import stats
import textdistance
import random
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm


def clean(tune):
    newStr = ""
    temp = ""
    for note in tune:
        if note.isalpha():
            newStr += note
            temp = note
        if note.isdigit():
            newStr += temp * ( int(note) - 1)
    return newStr


# Round output values to available values in D major
def samples_to_d_major(samples):
    def note_to_d_major(note):
        d_maj_values = np.array([62, 64, 66, 67, 69, 71, 73]) - 60  # C is now at 0
                                # D   E   F   G   A   B   C
        octave = note // 12
        noteInScale = note % 12

        noteDistances = np.abs(d_maj_values - noteInScale)
        roundedNote = d_maj_values[noteDistances.argmin()]
        return roundedNote + 12 * octave

    note_to_d_major = np.vectorize(note_to_d_major)
    return note_to_d_major(samples).astype(np.int32)


def nums_to_abc(nums):
    chars = []
    #     print(nums)
    for num in nums:
        if num in notes:
            chars.append(notes[num])
        elif num > 83:
            apostrophe_count = np.ceil((num - 83) / 12).astype(np.int32)
            apostrophe_count = np.asscalar(apostrophe_count)
            note = notes[num - 12 * apostrophe_count]
            apostrophes = "".join(["'"] * apostrophe_count)
            chars.append(note + apostrophes)
        elif num < 60:
            comma_count = np.ceil((60 - num) / 12).astype(np.int32)
            comma_count = np.asscalar(comma_count)
            note = notes[num + 12 * comma_count]
            commas = "".join([","] * comma_count)
            chars.append(note + commas)
        else:
            print("ya fucked up: {} not in notes".format(num))

    return chars


def tune_to_abc(tune):
    bars = [nums_to_abc(bar) for bar in tune]
    return bars


def get_stats(arr, title):
    data_similarities = []
    num = 1
    for i in range(len(arr) - 2):
        for j in range(i + 1, len(arr) - 1):
            num += 1
            print('iteration ', num, ' of ', ( len(arr) * (len(arr) - 1)))
            data_similarities.append(textdistance.damerau_levenshtein.normalized_distance(arr[i], arr[j]))

    np.save(title+'.npy', data_similarities)
    #print_stats(data_similarities, title)


def print_stats(arr, title):
    print(stats.describe(arr))
    plot(arr, title)


def plot(arr, title):
    sns.set(style="whitegrid")
    #sns.distplot(arr, norm_hist=False, kde=False)
    #plt.title(title)
    sns.boxplot(arr)
    #plt.ylabel('count')
    plt.xlabel('normalized distance')
    text = ' (mean = ' + str(round( np.mean(arr), 4)) + ', variance = ' + str(round( np.var(arr), 4)) + ')'
    plt.title(title + text)
    plt.savefig(title+'box_plots.png')
    plt.show()


"""
# Dataset stats
with open('./../Generation/abcTunes.txt', 'r') as f:
    tunesList = f.readlines()

newTunesList = []
for tune in tunesList:
    newTune = clean(tune)
    newTunesList.append(newTune)

myList = [x for x in newTunesList if len(x) == 256]
sampling = random.choices(myList, k=100)

get_stats(sampling, 'dataset')


# Generator stats
gen = tf.keras.models.load_model('./Trained/generator_best.h5')
noise = np.random.normal(0, 1, [100, 100]) #20 arrays of noise of shape [100,]
samples = gen.predict(noise)
samples = np.squeeze(samples,-1)

NOTE_MIN = 53
NOTE_MAX = 93

halfMaxPitch = (NOTE_MAX+NOTE_MIN)//2
pitchRange = NOTE_MAX - halfMaxPitch

samples = (samples * pitchRange) + halfMaxPitch
tunes_generated = np.rint(samples).astype(np.int)
tunes_generated = samples_to_d_major(tunes_generated)

chars_as_num = {
    'F,': 54,
    'G,': 55,
    'A,': 57,
    'B,': 59,
    'C,': 61,
    'D': 62,
    'E': 64,
    'F': 66,
    'G': 67,
    'A': 69,
    'B': 71,
    'C': 73,
    'd': 74,
    'e': 76,
    'f': 78,
    'g': 79,
    'a': 81,
    'b': 83,
    'c': 85,
    'd\'': 86,
    'e\'': 88,
    'f\'': 90
}

notes = {v:k for (k,v) in chars_as_num.items()}
tunes = [tune_to_abc(tune) for tune in tunes_generated]
songs = []

for tune in tunes:
    myStr = ""
    for phrases in tune:
        for notes in phrases:
            myStr += notes
    songs.append(myStr)

get_stats(songs, 'generated')
"""

dataset = np.load('dataset.npy')
generated = np.load('generated.npy')

plot(dataset, 'dataset')
plot(generated, 'generated')