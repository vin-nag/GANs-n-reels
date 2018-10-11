# Author: Caleb Graves
from music21.pitch import AccidentalException
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer
from src.Generation.Decoding import Audio_Converter
from src.Generation.Vectorizing import Vectorizer as Vec
import matplotlib.pyplot as plt
import numpy as np
import random
import keras

VECTOR_DIR = '../../../Data/Vectors/'

MAX_PITCH = 80
MIN_PITCH = 53
MID_PITCH = (MAX_PITCH + MIN_PITCH) / 2
RANGE = MAX_PITCH - MIN_PITCH

tritone = {0: 'z[=G2=G,2][=G2=G,2][=G2=G,2][_E8_E,8] z[=F2=F,2][=F2=F,2][=F2=F,2][=D8=D,]'}


def load_vector(fname):
    fname = VECTOR_DIR + fname
    try:
        array = np.load(fname)
    except FileNotFoundError:
        array = []

    return array


num_as_chars = inv_map = {v: k for k, v in Vec.chars_as_num.items()}


def convert_note_list(lst):
    """
    Converts a vectorized tune to ABC
    :param lst: The list of bars in the tune
    :return: The ABC string
    """
    out = ''
    for x in lst:
        append = ''
        hold = ''
        num = x[0]
        if not (num == 0 or (60 <= num <= 83)):
            if num > 83:
                mult = (num - 72) // 12
                append = '\'' * mult
                num = num - (12 * mult)
            else:  # x[0] < 60
                mult = ((num - 60) // 12) * -1
                append = ',' * mult
                num = num + (12 * mult)

        if num not in num_as_chars:
            num = num - 1
            prepend = '^'
        else:
            prepend = '='

        char = num_as_chars[num]

        if len(x) != 1: hold = str(len(x))
        out += prepend + char + append + hold
    return out


def decode_single_vector(array, presentation):
    """
    Takes an array of tunes in vectorized form and returns a dictionary of abc strings.
    :param array: A 3 dimensional array of pieces, in the form pieces[tune][bar]
    :return: A dictionary of abc strings.
    """

    def decode_song(vec):
        dur = [vec[0][0]]
        master = []
        for x in vec:
            for y in x:
                if y == dur[0]:
                    dur.append(y)
                else:
                    master.append(dur)
                    dur = [y]
        return master

    if presentation:
        print("Loading Vector Results from GAN...\n")
        print("Selected Vector Generated")
        print(array[0])
        print("\nImage of the Vector")
        plt.matshow(array[0].T, cmap=plt.get_cmap('Greys'), fignum=1)
        plt.show()

    tunes = dict()
    c = 0
    for x in array:
        tune = decode_song(x)
        tunes[c] = convert_note_list(tune)
        c += 1

    if presentation:
        print("Decoding Vectors to ABC format...")
        print(" ")
        print("ABC Notation Generated")
        print(tunes[0])
        print(" ")

    return tunes


def parse_raw_abc(abc):
    import re

    abc = abc.replace('|', '')
    vec = re.findall('([_=^]*[a-gzA-G][,\']*[\d]*/?[\d]*)', abc)
    prev = vec[0]
    tune = []
    c = 0
    for x in vec:
        if x == prev:
            c += 1
        else:
            tune.append(prev + str(c)) if c != 1 else tune.append(prev)
            prev = x
            c = 1
    tune = ''.join(tune)
    print(tune)
    return tune


class Decoder:
    """
    A class which helps control the variables for playing the music.
    """
    def __init__(self, pitches, timing, tunes, time='1/48', key='Cmaj', gan=None):
        self.time = time
        self.key = key
        self.pitches = pitches
        self.timing = timing
        self.tunes = tunes
        self.gan = gan
        self.header = '''X: 1\nT: AI Music\nR: reel\nM: 4/4\nL: {}\nK: {}\n'''.format(self.time, self.key)

    def set_key(self, key):
        self.key = key

    def set_time(self, time):
        self.time = time

    def save_tune(self, num, out='mid'):
        abc = self.header + self.tunes[num]
        tune = converter.parse(abc, format='abc')
        for p in tune.parts: p.insert(0, instrument.Flute())
        switch = Audio_Converter.Converter(tune, out_type=out, num=num)
        switch.save_song()

    def play(self, num=None, save=False, autosave=False):
        """
        This function takes in a song in ABC format string and plays it using music21 and pygame modules
        Note: Timidity must also be installed, as it's config file is required for the stream object.
        :param num: index of the ABC song
        :param save: If true, prompts the user if they want to save the tune after playing.
        superseded by autosave
        :param autosave: If true, automatically save the song after playing it.
        :return: None
        """

        if num is None: num = random.randint(0, len(self.tunes)-1)
        abc = self.header + self.tunes[num]

        try:
            # convert abc format to stream object and add the harp instrument
            tune = converter.parse(abc, format='abc')
            for p in tune.parts: p.insert(0, instrument.Flute())

            # Emit a tone to break up consecutive plays
            player = StreamPlayer(converter.parse(self.header + 'z12C12z12', format='abc'))
            player.play()

            # play music using pygame stream player
            player = StreamPlayer(tune)
            print("Playing tune #{}\nABC:   {}\n".format(num, self.tunes[num]))
            player.play()

            if autosave:
                self.save_tune(num)
            elif save and input('Would you like to save the song as a MIDI file? Y/N:   ').upper() == 'Y':
                self.save_tune(num)
        except AccidentalException:
            print('Accidental Exception thrown in ABC:')
            print(abc)

    def play_all(self, save=False, autosave=False):
        for x in range(len(self.tunes)): self.play(x, save, autosave)

    def play_infinite(self, save=False, autosave=False):
        while True:
            self.play_all(save, autosave)
            if self.gan: self.refresh_tunes()

    def songs_to_greyscale(self, numcols=3, out='bars_bw.png'):
        """
        Takes an array of vectorized tunes and return an image representation of them.
        :param numcols: Number of columns; Default -> 3
        :param out: Name of output file; Default -> 'bars_bw.png'
        :return: None. Saves an image to disk.
        """
        size = len(self.pitches)

        if size == 0:
            print("No pitches found. Aborting.")
            return

        f, axs = plt.subplots(size, numcols, figsize=(10, size * 2))
        plt.tight_layout()
        for num, song in enumerate(self.pitches):
            img = song[:16]
            width = img.shape[1]
            index = num * numcols + 1
            plt.subplot(size, numcols, index)
            plt.axis('off')
            plt.title("1 bar per line", fontsize=10)
            plt.matshow(img.reshape(16, width), cmap='gray', interpolation='nearest', fignum=0, aspect="auto")
            plt.subplot(size, numcols, index + 1)
            plt.axis('off')
            plt.title("2 bars per line", fontsize=10)
            plt.matshow(img.reshape(8, width * 2), cmap='gray', interpolation='nearest', fignum=0, aspect="auto")
            plt.subplot(size, numcols, index + 2)
            plt.axis('off')
            plt.title("4 bars per line", fontsize=10)
            plt.matshow(img.reshape(4, width * 4), cmap='gray', interpolation='nearest', fignum=0, aspect="auto")
        plt.savefig('../../../Data/Images/' + out)

    def refresh_tunes(self, presentation=False):
        if self.gan:
            noise = np.random.normal(0, 1, [1, 100])  # 20 arrays of noise of shape [100,]
            generated_samples = self.gan.predict(noise)
            generated_samples = generated_samples[:, :-1, 4:-4]
            generated_samples = np.squeeze(generated_samples, axis=3)  # Remove colour channel
            generated_samples = generated_samples.reshape([-1, 16, 16])

            # Map from [-1, 1] to [MIN_PITCH, MAX_PITCH]
            generated_samples = (RANGE * generated_samples) + MID_PITCH

            # Make values discrete
            generated_samples = generated_samples.astype(np.int32)
            self.pitches = decode_single_vector(generated_samples, False)
            self.tunes = decode_single_vector(self.pitches, presentation)
        else:
            print("Failed to update songs.")

    @classmethod
    def from_raw_abc(cls, abc, time='1/8', key='Cmaj', presentation=False, override=False):
        import src.Generation.Cleaning.Cleaner as clean
        abc = clean.clean(abc, 0)
        if override:
            tunes = {0: abc}
        else:
            if abc == '!!BAD ABC!!':
                tunes = tritone
            else:
                tunes = {0: abc}

        return cls([], [], tunes, time, key)

    @classmethod
    def from_dict(cls, tunes, time='1/8', key='Cmaj', presentation=False):
        try:
            tunes = {x: tunes[x]['abc'] for x in tunes}
        except IndexError:
            tunes = tritone

        return cls([], [], tunes, time, key)

    @classmethod
    def from_h5(cls, generator="../src/Model/Trained/generator.h5", time='1/48', key='Cmaj', presentation=False):
        gan = keras.models.load_model(generator)
        obj = cls([], [], [], time, key, gan=gan)
        obj.refresh_tunes(presentation)
        return obj

    @classmethod
    def from_single_vector(cls, pitches, time='1/48', key='Cmaj', presentation=False):
        if type(pitches) == str: pitches = load_vector(pitches)
        tunes = decode_single_vector(pitches, presentation)

        if presentation:
            print("Sample Image of Vector:")
            plt.matshow(pitches[0].T, cmap=plt.get_cmap('Greys'), fignum=1)
            plt.show()
            print("ABC Notation Sample:")
            print(tunes[0] + '\n')

        return cls(pitches, [], tunes, time, key)


if __name__ == '__main__':
    drowsy_maggie = '''|:E2BE dEBE|E2BE AFDF|E2BE dEBE|1 BABc dAFD:|2 BABc dAFA||
                    |:d2fd cdec|defg afge|1 d2fd c2ec|BABc dAFA:|2 afge fdec|BABc dAFA||
                    |:dBfB dBfB|cAeA cAeA|1 dBfB dBfB|defg aece:|2 defg aecA|BABc dAFA||
                    |:dffe dfBf|ceed ceAe|1 dffe defg|a2ag aece:|2 af=ge fdec|BABc dAFD||'''

    rand_tune = """A,A,B,A,A,A,G,G,G,A,B,B,CB,EE|EEAAffeeddBBGGFF|EEFFEEBAGGAAGGGG|ccccdeeeddBBGGAA|ggeeccfeAABBBBFF|ccAAddddddccGGFF|DDEECB,B,B,D,E,B,B,CCCC|B,B,CB,A,A,FFDDDDEEGG|ddcccBGFGGBBFFcd|ddccefggccAGB,CBB|AAAAddfeffBBffAG|AABBBBFFCCB,B,CCCB,|A,A,B,B,B,CEEGGDCFFAA|DDFFDDcBAAGFB,B,cc|cBccaaabfgfgBcee|AAGGEECB,B,B,B,A,CCA,G,"""

    # decode = Decoder.from_raw_abc(drowsy_maggie, key='Dmaj')
    # decode.play()

    # decode = Decoder.from_dict({0: {'abc': drowsy_maggie}}, key='Dmaj')
    # decode.play()

    # decode = Decoder.from_raw_abc(parse_raw_abc(rand_tune), override=True, time='1/4')
    # decode.play()

    # decode = Decoder.from_single_vector('Major_Tunes_Generated_Oct11.npy', time='1/48')
    # decode.play(0)
    # decode.play_all()
    # decode.test_play_all()
    # decode.save_tune(1, out='mid')
    decode = Decoder.from_h5()
    decode.play_infinite()
