from src.Generation.Decoding.Decoding import Decoder
import numpy as np


def demo_helper():
    # decoder = Decoder.from_h5()
    decoder = Decoder.from_single_vector(np.load("generated_notes.npy"), time="1/16")
    decoder.set_time('1/16')
    #decoder.play(0)
    decoder.save_tune(0)

if __name__ == '__main__':
    demo_helper()