import pandas as pd
import numpy as np
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

def decode_single(tunes):

    tunes = pd.DataFrame.from_dict(tunes, orient='index')
    tunes = Vectorizer.vectorize_frame(tunes, bar_subdivision=48)
    tune = tunes.loc[tunes['setting'] == str(setting)]['notes']
    print(tune)
    tune = np.array(tune)
    print(tune)
    print(tune[0].shape)
    Decoding.pitches_to_img(tune, out='Tune_' + str(setting))

if __name__ == '__main__':
    tunes = {
        1: {'type': 'reel', 'mode': 'Cmajor', 'tune': '1', 'setting': '1',
              'abc': "E3A6^A2c2B2^FG^ABe2AG^AA^c2F^FD2^DE^CC2B,D^DE2^G^ABc2B2^Ac2A2E4F2EF3G^FE2A3^AA2^A2c2B2G2c^ca2^g2f2^f^g2ac'b^c'c'^d'd'^a^gefe2Bcd2c2B2A^A^G2E2G2^A2F^F4FE2A2^A2A^G^A2c2B2G2B^A^d2^G2A^Gc^cF^FD^DE2D^CDB,DE3^G^Ac2Bc^AB3A^GEF^DEF4^FGF2E2A6^A2c2B^AG2B^A^ffBc2^cA2^d2^ga^ga^aag^ffefec2d2B2cB^ABA2^DEF2^FF^F2G2^F",
              'meter': '4/4'},
        2: {'type': 'reel', 'mode': 'Cmajor', 'tune': '2', 'setting': '2',
            'abc': '^D2EF2D2C2D2A^Gf^f^g2a2g2^c2Bcd2^c2G2c2E2F2B,4E2c^c^f2g2^f2f2^F2F^FE2^A,A,^G,2F,2E^D^FG^D2B,2D^CA2f2^g4g2c2Bc^cdc2G2B2FEF2B,2^A,2E2c2^f6e2^FG^FFE^D^A,2^F,2E,2^cd^c2c2^A2cBF^Fc^cA^G3E4A2B2^F2C2E2^G2^D2^C2^FGd^cc2f2g2^f2^deF^F3^DD^A,2G,^G,F,2^d2^c2c3B3ABdcBc^F^DA^Gg^fc^dB2^FFD^DE2^GG^D2^C2^F2d2c2f2^ggf2e2F2^F2^DE^A,2^F,G,2',
            'meter': '4/4'}
    }
    decode_single(tunes)
