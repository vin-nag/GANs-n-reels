# Author: Caleb Graves
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer

class Decoder():

    def __init__(self):

        self.header = 'X: 1\nT: AI Music\nR: reel' + \
                        '\nM: 4/4\nL: 1/8\nK: Dmaj\n'
        return

    def play(self, input):
        """
        This function takes in a song in ABC format string and plays it using music21 and pygame modules
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
