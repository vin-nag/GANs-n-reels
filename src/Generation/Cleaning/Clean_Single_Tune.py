import pandas as pd
import numpy as np
from Data.Clean.Common_Time import tunes
from src.Generation.Cleaning.Cleaner import clean
from src.Generation.Vectorizing import Vectorizer
from src.Generation.Decoding import Decoding

#setting = 12410
setting = 13542

if setting == 13542: tunes[setting]['abc'] = clean("""E>A-A>^G A2 (3Bcd | (3efe e>c d2 c>d | e>A (3AAA A>B (3cBA | B>cB>A G2- G>=F |
E2 A2 A>Bc>d | e2 e>c d4 | e>a (3aaa a>ge>d | =c2 A2 A4 :|
g2 g>a g>fe>f | g>fe>c d>Bc>d | e>A-A>^G A>Bc>A | B>^GE>F G2 F>G |
E>A (3AAA A>Bc>d | e2- e>c d>B (3Bcd | e2 a2 a>ge>d | =c>AA>^G A4 :| 
""")

tunes = pd.DataFrame.from_dict(tunes, orient='index')
tunes = Vectorizer.vectorize_frame(tunes, bar_subdivision=48)
tune = tunes.loc[tunes['setting'] == str(setting)]['notes']
print(tune)
tune = np.array(tune)
print(tune)
print(tune[0].shape)
Decoding.pitches_to_img(tune, out='Tune_' + str(setting))

if __name__ == '__main__':
    pass