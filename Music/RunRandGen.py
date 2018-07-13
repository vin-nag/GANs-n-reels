#!/home/mitchell/anaconda3/bin/python3

# Envoke RandomSongGen.py

import RandomSongGen

# Input desired option here (0 = random, 1 = statistics, 2 = type/time restriction)
gen = RandomSongGen.RandomGenerator(2)
# Input the desired amount of songs to generate
songs = gen.generateSongs(5)

#for x in songs:
    #print(songs[x])
