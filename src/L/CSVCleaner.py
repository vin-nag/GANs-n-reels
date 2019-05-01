
songs = []

with open('generated_tunes.csv', 'r') as f:

    f.readline()

    for line in f:

        songs.append(line.split(',')[1])

newsongs = []

for song in songs:

    bars = song.split('|')

    newbars = []

    for bar in bars:

        # print("Original: {}".format(bar))

        test = []
        i = 0
        while i < len(bar):
            if bar[i] == '^':
                test.append(bar[i:i+2])
                i += 1
            else:
                test.append(bar[i])
            i += 1

        bar = test

        newbar = ''

        i = 0
        count = 1
        note = None

        while i < len(bar):

            # print(i)
            if note != bar[i]:
                if count > 1:
                    newbar += str(count)
                    count = 1
                note = bar[i]
                newbar += bar[i]
            else:
                count += 1
                if i % 4 == 0:
                    if count > 2:
                        newbar += str(count - 1)
                    count = 1
                    note = bar[i]
                    newbar += bar[i]
            i += 1
        if count > 1:
            newbar += str(count)

        # print("Updated: {}".format(newbar))
        newbars.append(newbar)

    newsongs.append('|'.join(newbars).replace('"', ''))

with open('cleaned_tunes.csv', 'w') as f:
    f.write(',tunes\n')
    for i, song in enumerate(newsongs):
        f.write('{},{}'.format(i, song))
