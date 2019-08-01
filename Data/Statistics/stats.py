from Data.Clean.Major_Tunes import tunes
import matplotlib.pyplot as plt

frequency = {}

for tune in tunes:
    str = tunes[tune]['abc']
    len = str.count('|')
    if len == 17:
        print(tunes[tune])
    if len in frequency:
        frequency[len] += 1
    else:
        frequency[len] = 1

plt.bar(frequency.keys(), frequency.values(), 2, color='g')
plt.show()