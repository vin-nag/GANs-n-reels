# Author: Caleb Graves
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer
import pandas as pd
import numpy as np

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


def condenser(pitches, held):
    x = 0
    master = []
    lst = list()
    while x < len(pitches):
        lst.append(pitches[x])
        x += 1
        if x == len(pitches) or held[x] == 1:
            master.append(lst)
            lst = []

    out = ''
    for x in master:
        prepend = ''
        append = ''
        hold = ''
        num = x[0]
        if not (num == 0 or (60 <= num <= 83)):
            if num > 83:
                mult = (num-72)//12
                append = '\'' * mult
                num = num - (12 * mult)
            else: # x[0] < 60
                mult = ((num-60)//12) * -1
                append = ',' * mult
                num = num + (12 * mult)

        if num not in number_notes:
            num = num - 1
            prepend = '^'

        char = number_notes[num]

        if len(x) != 1: hold = str(len(x))
        out += prepend + char + append + hold
    return out


class Decoder():

    def __init__(self, time='1/48', key='Cmaj'):

        self.time = time
        self.key = key

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

    def play_from_dict(self, dic):
        self.set_key(dic['mode'])
        self.set_time('1/8')
        self.play(dic['abc'])

    def play_from_vector(self, vec):
        self.set_key('Cmaj')
        self.set_time('1/48')
        abc = condenser(list(vec['note']), list(vec['timing']))
        self.play(abc)

    def play(self, abc):
        """
        This function takes in a song in ABC format string and plays it using music21 and pygame modules
        Note: Timidity must also be installed, as it's config file is required for the stream object.
        :param abc: Generated song in ABC format
        :return: None
        """

        abc = self.gen_header() + abc

        # convert abc format to stream object
        tune = converter.parseData(abc, format='abc')

        # add harp instrument
        for p in tune.parts:
            p.insert(0, instrument.Harp())

        # play music using pygame stream player
        player = StreamPlayer(tune)
        player.play()

        return


if __name__ == '__main__':
    drowsy_maggie = '''|:E2BE dEBE|E2BE AFDF|E2BE dEBE|1 BABc dAFD:|2 BABc dAFA||
                    |:d2fd cdec|defg afge|1 d2fd c2ec|BABc dAFA:|2 afge fdec|BABc dAFA||
                    |:dBfB dBfB|cAeA cAeA|1 dBfB dBfB|defg aece:|2 defg aecA|BABc dAFA||
                    |:dffe dfBf|ceed ceAe|1 dffe defg|a2ag aece:|2 af=ge fdec|BABc dAFD||'''

    decode = Decoder(time='1/8')
    decode.play(drowsy_maggie)
