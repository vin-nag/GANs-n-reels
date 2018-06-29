# Author: Caleb Graves
from music21 import converter
from music21 import instrument
from music21.midi.realtime import StreamPlayer

class Decoder():

    def __init__(self):

        self.header = 'X: 1\nT: AI Music\nR: reel' + \
                        '\nM: 4/4\nL: 1/8\nK: Dmaj\n'
        return

    def decode(self, input):

        input = self.header + input

        tune = converter.parseData(input, format='abc')

        for p in tune.parts:
            p.insert(0, instrument.Harp())

        player = StreamPlayer(tune)
        player.play()

        return



song = "|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|"
decoder = Decoder()
decoder.decode(song)
