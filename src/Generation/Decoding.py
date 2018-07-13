# Author: Caleb Graves
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer

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

    def __init__(self):

        self.header = '''X: 1\n
                        T: AI Music\n
                        R: reel\n
                        M: 4/4\n
                        L: 1/48\n
                        K: Dmaj\n'''
        return

    def play(self, input):
        """
        This function takes in a song in ABC format string and plays it using music21 and pygame modules
        Note: Timidity must also be installed, as it's config file is required for the stream object.
        :param input: Generated song in ABC format
        :return: None
        """

        input = self.header + input

        # convert abc format to stream object
        tune = converter.parseData(input, format='abc')

        # add harp instrument
        for p in tune.parts:
            p.insert(0, instrument.Harp())

        # play music using pygame stream player
        player = StreamPlayer(tune)
        player.play()

        return
