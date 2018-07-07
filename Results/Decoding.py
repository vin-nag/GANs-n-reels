# Author: Caleb Graves
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer

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
