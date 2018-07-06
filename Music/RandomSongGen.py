#!/usr/bin/python

# A random ABC generator

import math
import random

amount = int(input('How many random songs do you want to generate? '))

notesHigh = ['C','D','E','F','G','A','B']
notesLow = ['c','d','e','f','g','a','b']
notesAll = notesHigh + notesLow
songs = {}

# Randomly genereate ABC notation
def GenerateABC():
    abc = ['|','|']
    abcOut = []
    measures = 16
    noteLen = 1/8
    beatPerMeasure = 4
    notesMes = 8
    choice = random.randint(1,2)
    for x in range(2):
        for y in range(notesMes):
            note = random.choice(notesAll)
            abc[x]+=note
    #Randomly choose either AABB or ABAB
    if choice == 1:
        abcOut = abc[0]+abc[0]+abc[1]+abc[1]
    else:
        abcOut = abc[0]+abc[1]+abc[0]+abc[1]
    abcOut = abcOut*4 + '|'
    return abcOut

# Randomly choose a song type
def randType():
    percentReel = 60
    number = random.randint(1,100)
    if number <= percentReel:
        type = 'reel'
    else:
        type = 'jig'
    return type

# Randomly choose a time signature
def randTime():
    percent44 = 50
    percent68 = 25
    percent34 = 12.5
    percent24 = 12.5
    number = random.randint(1,100)
    if number <= percent44:
        time = '4/4'
    elif number <= percent44 + percent68:
        time = '6/8'
    elif number <= percent44 + percent68 + percent34:
        time = '3/4'
    else:
        time = '2/4'
    return time

# Randomly chose a key
def randMode():
    number = random.randint(1,2)
    if number == 1:
        mode = 'Gmajor'
    else:
        mode = 'Dmajor'
    return mode

# Generate the random songs
for x in range(0,amount):
    num = x
    title = 'Random Song #'+str(x)
    type = randType()
    timeSig = randTime()
    noteLen = '1/8'
    key = randMode()
    abc = GenerateABC()
    songs[x] = {'X':x, 'T':title, 'R':type, 'M':timeSig, 'L':noteLen, 'K':key, 'A':abc}

# Print the songs
for x in songs:
    print(songs[x])
