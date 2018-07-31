from src.Generation.Decoding import Decoding


def demo_helper(vec):
    decoder = Decoding.Decoder()
    Decoding.pitches_to_img(vec, out='Display.png')
    abc_dic = Decoding.decode_single_vector(vec)
    decoder.set_time('1/16')
    decoder.play_from_dict(abc_dic[0])

if __name__ == '__main__':
    pass