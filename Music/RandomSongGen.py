#!/home/mitchell/anaconda3/bin/python3

# A random ABC generator

import math
import random

class RandomGenerator:
    
    # Pass in option when initalizing the class. 0 = random, 1 = statistics, 2 = type/time restriction
    # Potential fourth option to limit note choices from keys
    def __init__(self, option):
        self.songs = {}
        self.option = option
        self.notesHigh = ['C','D','E','F','G','A','B']
        self.notesLow = ['c','d','e','f','g','a','b']
        self.notesAll = self.notesHigh + self.notesLow
        # Accidentals that come before the note and have no effect on timing of notes
        self.accidentalsBefore = ['^' , '=' , '_']
        # Accidentals that come after the note and have no effect on timing of notes
        # For 11k songs: ' = 3700  , = 20k
        self.accidentalsAfter = [',' , '\'']
        # Accidentals that effect a notes length
        self.accidentalsTime = [['<'] + ['>']]

    # Randomly genereate ABC notation
    def generateABC(self, timeSignature):
        abc = ['|','|']
        abcOut = []
        measures = 16
        noteLen = 1/8
        beatPerMeasure = 4
        notesMes = 8
        choice = random.randint(1,2)
        if self.option == 0:
            for x in range(2):
                for y in range(notesMes):
                    note = random.choice(self.notesAll)
                    accBf = random.choice(self.accidentalsBefore)
                    accAf = random.choice(self.accidentalsAfter)
                    abc[x] += (accBf + note + accAf)
        elif self.option == 1:
            for x in range(2):
                for y in range(notesMes):
                    note = random.choice(self.notesAll)
                    randIntAf = random.randint(0,100)
                    randIntBf = random.randint(0,100)
                    if randIntBf <= 2:
                        accBf = random.choice(self.accidentalsBefore)
                    else:
                        accBf = ''
                    if randIntAf <= 2:
                        accAf = random.choice(self.accidentalsAfter)
                    else:
                        accAf = ''
                    abc[x] += (accBf + note + accAf)
        elif self.option == 2:
            time = timeSignature.split('/')
            # Note value for one beat (Time signature 'denominator')
            beat = int(time[1])
            # noteMult give factor to multiply time sig 'numerator' by to get how many 1/8th notes per measure
            noteMult = 8 // beat
            notesMes = int(time[0]) * noteMult
            for x in range(2):
                for y in range(notesMes):
                    note = random.choice(self.notesAll)
                    randIntAf = random.randint(0,100)
                    randIntBf = random.randint(0,100)
                    if randIntBf <= 2:
                        accBf = random.choice(self.accidentalsBefore)
                    else:
                        accBf = ''
                    if randIntAf <= 2:
                        accAf = random.choice(self.accidentalsAfter)
                    else:
                        accAf = ''
                    abc[x] += (accBf + note + accAf)                                           
        #Randomly choose either AABB or ABAB
        if choice == 1:
            abcOut = abc[0]+abc[0]+abc[1]+abc[1]
        else:
            abcOut = abc[0]+abc[1]+abc[0]+abc[1]
        abcOut = abcOut*4 + '|'
        return abcOut

    # Randomly choose a song style
    def randStyle(self):
        if self.option == 0:
            style = random.choice(
                ['hornpipe']*1 \
                + ['slip jig']*1 \
                + ['mazurka']*1 \
                + ['three-two']*1 \
                + ['waltz']*1 \
                + ['polka']*1 \
                + ['strathspey']*1 \
                + ['barndance']*1 \
                + ['slide']*1 \
                + ['reel']*1 \
                + ['jig']*1 \
            )
        elif self.option == 1 or 2:
            # Percentages are multiplied by 100 to give ints
            style = random.choice(
                ['hornpipe']*727 \
                + ['slip jig']*378 \
                + ['mazurka']*133 \
                + ['three-two']*92 \
                + ['waltz']*718 \
                + ['polka']*733 \
                + ['strathspey']*302 \
                + ['barndance']*502 \
                + ['slide']*238 \
                + ['reel']*3713 \
                + ['jig']*2460 \
            )
        return style

    # Randomly choose a time signature
    def randTime(self):
        if self.option == 0:
            time = random.choice(
                ['2/4']*1 \
                + ['3/2']*1 \
                + ['12/8']*1 \
                + ['9/8']*1 \
                + ['4/4']*1 \
                + ['3/4']*1 \
                + ['6/8']*1 \
            )
        elif self.option == 1:
            time = random.choice(
                ['2/4']*733 \
                + ['3/2']*92 \
                + ['12/8']*238 \
                + ['9/8']*378 \
                + ['4/4']*5245 \
                + ['3/4']*851 \
                + ['6/8']*2460 \
            )
        return time

    def styleTime(self, style):
        # https://thesession.org/discussions/33221
        if style == 'hornpipe':
            time = '4/4'
        elif style == 'slip jig':
            time = '9/8'
        elif style == 'mazurka':
            time = '3/4'
        elif style == 'three-two':
            time = '3/2'
        elif style == 'waltz':
            time = '3/4'
        elif style == 'polka':
            time = '2/4'
        elif style == 'strathspey':
            time = '4/4'
        elif style == 'barndance':
            time = '4/4'
        elif style == 'slide':
            time = '12/8'
        elif style == 'reel':
            time = '4/4'
        elif style == 'jig':
            time = '6/8'
        return time

    # Randomly chose a key
    def randMode(self):
        if self.option == 0:
            mode = random.choice(
                ['Gdorian']*1 \
                + ['Edorian']*1 \
                + ['Dmajor']*1 \
                + ['Emixolydian']*1 \
                + ['Ddorian']*1 \
                + ['Amixolydian']*1 \
                + ['Cmajor']*1 \
                + ['Emajor']*1 \
                + ['Gmajor']*1 \
                + ['Dminor']*1 \
                + ['Gminor']*1 \
                + ['Cdorian']*1 \
                + ['Fdorian']*1 \
                + ['Bmixolydian']*1 \
                + ['Bminor']*1 \
                + ['Adorian']*1 \
                + ['Aminor']*1 \
                + ['Gmixolydian']*1 \
                + ['Amajor']*1 \
                + ['Fmajor']*1 \
                + ['Dmixolydian']*1 \
                + ['Bdorian']*1 \
                + ['Eminor']*1 \
            )
        elif self.option == 1 or 2:
            mode = random.choice(
                ['Gdorian']*78 \
                + ['Edorian']*442 \
                + ['Dmajor']*2676 \
                + ['Emixolydian']*16 \
                + ['Ddorian']*96 \
                + ['Amixolydian']*331 \
                + ['Cmajor']*239 \
                + ['Emajor']*51 \
                + ['Gmajor']*2797 \
                + ['Dminor']*133 \
                + ['Gminor']*134 \
                + ['Cdorian']*23 \
                + ['Fdorian']*19 \
                + ['Bmixolydian']*5 \
                + ['Bminor']*347 \
                + ['Adorian']*575 \
                + ['Aminor']*298 \
                + ['Gmixolydian']*40 \
                + ['Amajor']*694 \
                + ['Fmajor']*157 \
                + ['Dmixolydian']*285 \
                + ['Bdorian']*29 \
                + ['Eminor']*525 \
            )
        return mode

    # Generate the random songs. num must be provided manually when invoking the function
    def generateSongs(self, num):
        for x in range(0,num):
            title = 'Random Song #'+str(x)
            style = self.randStyle()
            if self.option == 2:
                timeSig = self.styleTime(style)
                abc = self.generateABC(timeSig)
            else:
                timeSig = self.randTime()
                abc = self.generateABC(timeSig)
            noteLen = '1/8'
            key = self.randMode()
            
            self.songs[x] = {'tune':x, 'setting':x, 'name':title, 'type':style, 'meter':timeSig, 'L':noteLen, 'mode':key, 'abc':abc}
        return self.songs
