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


song = "|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|G'E,CG,G,c'a,_b,|G'E,CG,G,c'a,_b,|E'bB'gb^A'e,d,|E'bB'gb^A'e,d,|"
song2 = "B,B,CB,AGEEB,B,B,B,B,B,D,D,|EEeeefccAAAADDB,B,|B,,A,,E,D,G,G,A,A,CCE,F,B,,B,,G,,G,,|F,,F,,F,,E,,B,,B,,A,,B,,G,,A,,B,,B,,D,D,G,F,|CCCB,AAEEB,B,CCB,B,D,D,|EEeeefBBAAAAEEdc|deefggaad'd'bc'bbAA|ccccccggagbbefff|f'f'g'f'abggeeddc'c'aa|g'g'bbffbbbbbbe'd'cc|CCB,B,EEA,A,G,A,CCA,A,F,F,|B,CCCF,F,F,F,A,A,DDGGcd|CCG,G,F,F,A,A,A,A,FFccdd|eeBBBBaaggggeedc|BBfegfeeFFEEEECC|F,F,A,A,CCAAEEagggab"

decoder = Decoder()
decoder.play(song2)
