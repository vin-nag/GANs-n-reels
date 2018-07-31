# Author: Caleb Graves
from music21.pitch import AccidentalException
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer
import matplotlib.pyplot as plt
import numpy as np
import random

VECTOR_DIR = '../../../Data/Vectors/'

tritone = {0: 'z[=G2=G,2][=G2=G,2][=G2=G,2][_E8_E,8] z[=F2=F,2][=F2=F,2][=F2=F,2][=D8=D,]'}


def load_vector(fname):
    fname = VECTOR_DIR + fname
    try:
        array = np.load(fname)
    except FileNotFoundError:
        array = []

    return array


number_notes = {
    60: 'C',
    62: 'D',
    64: 'E',
    65: 'F',
    67: 'G',
    69: 'A',
    71: 'B',
    72: 'c',
    74: 'd',
    76: 'e',
    77: 'f',
    79: 'g',
    81: 'a',
    83: 'b',
    0: 'z'
}


def convert_note_list(lst):
    """
    Converts a vectorized tune to ABC
    :param lst: The list of bars in the tune
    :return: The ABC string
    """
    out = ''
    for x in lst:
        prepend = ''
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

        if num not in number_notes:
            num = num - 1
            prepend = '^'

        char = number_notes[num]

        if len(x) != 1: hold = str(len(x))
        out += prepend + char + append + hold
    return out


class Decoder:
    """
    A class which helps control the variables for playing the music.
    """
    def __init__(self, pitches, timing, tunes, time='1/48', key='Cmaj'):
        self.time = time
        self.key = key
        self.pitches = pitches
        self.timing = timing
        self.tunes = tunes

    def gen_header(self):
        header = '''X: 1\n
                    T: AI Music\n
                    R: reel\n
                    M: 4/4\n
                    L: ''' + self.time + '''\n
                    K: ''' + self.key + '''\n'''
        return header

    def set_key(self, key):
        self.key = key

    def set_time(self, time):
        self.time = time

    def play(self, num=None):
        """
        This function takes in a song in ABC format string and plays it using music21 and pygame modules
        Note: Timidity must also be installed, as it's config file is required for the stream object.
        :param num: index of the ABC song
        :return: None
        """

        if not num: num = random.randint(0, len(self.tunes)-1)
        abc = self.gen_header() + self.tunes[num]

        try:
            # convert abc format to stream object and add the harp instrument
            tune = converter.parse(abc, format='abc')
            for p in tune.parts: p.insert(0, instrument.Flute())

            # play music using pygame stream player
            player = StreamPlayer(tune)
            print("Playing tune #{}\nABC:   {}\n".format(num, self.tunes[num]))
            player.play()

            player = StreamPlayer(converter.parse(self.gen_header() + 'z12C12z12', format='abc'))
            player.play()
        except AccidentalException:
            print(abc)

    def play_all(self):
        for x in range(len(self.tunes)): self.play(x)

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

    def songs_to_colour(self, numcols=3, out='bars_cl.png'):
        """
        Takes an array of vectorized tunes and return an image representation of them.
        :param numcols: Number of columns; Default -> 3
        :param out: Name of output file; Default -> 'bars_cl.png'
        :return: None. Saves an image to disk.
        """
        print("This is a stub!")
        return

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
    def from_single_vector(cls, pitches, time='1/48', key='Cmaj', presentation=False):

        def decode_single_vector(array):
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

        if type(pitches) == str: pitches = load_vector(pitches)
        tunes = decode_single_vector(pitches)

        if presentation:
            print("Sample Image of Vector:")
            plt.matshow(pitches[0].T, cmap=plt.get_cmap('Greys'), fignum=1)
            plt.show()
            print("ABC Notation Sample:")
            print(tunes[0] + '\n')

        return cls(pitches, [], tunes, time, key)

    @classmethod
    def from_double_vector(cls, pitches, timing, time='1/48', key='Cmaj', presentation=False):

        def decode_dual_vector(pitches, timing):
            # TODO - Finish

            def decode_song(pitches, timing):
                x = 0
                master = []
                lst = list()
                while x < len(pitches):
                    lst.append(pitches[x])
                    x += 1
                    if x == len(pitches) or timing[x] == 1:
                        master.append(lst)
                        lst = []

                return master

            songs = dict()
            for c in range(pitches.shape[0]):
                tune = decode_song(pitches[c], timing[c])
                songs[c] = convert_note_list(tune)
            return songs

        if type(pitches) == str: pitches = load_vector(pitches)
        if type(timing) == str: timing = load_vector(timing)

        return cls(pitches, timing, decode_dual_vector(pitches, timing), time, key)


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


def decode_single_vector_no_file(array, num=0, presentation=False):

    if (presentation):
        print("Loading Vector Results from GAN...")
        print(" ")
        print("Selected Vector Generated")
        print(array[num])
        print(" ")
        print("Image of the Vector")
        plt.matshow(array[0].T, cmap=plt.get_cmap('Greys'), fignum=1)
        plt.show()

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

    songs = dict()
    c = 0
    for x in array:
        tune = decode_song(x)
        songs[c] = convert_note_list(tune)
        c += 1

    if(presentation):
        print("Decoding Vectors to ABC format...")
        print(" ")
        print("ABC Notation Generated")
        print(songs[num])
        print(" ")

    return songs


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

    decode = Decoder.from_single_vector('generated_notes_July30_V3.npy', time='1/48', presentation=True)
    #decode.play_all()
    decode.play(4)
    decode.play(9)
