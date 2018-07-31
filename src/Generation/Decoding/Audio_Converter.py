from midi2audio import FluidSynth
from pydub import AudioSegment

# TODO - Save the tune
default = '../../../Data/Audio/'


class Converter:
    """
    This module requires other audio packages to function:
    midi2audio
    FluidSynth
    pydub
    FFmpeg
    """
    def __init__(self, tune, out_type='mid', num=0):

        self.out_type = self.parse_out_type(out_type)
        self.tune = tune
        self.num = num

        if type(tune) == str:
            parts = tune.split('.')
            if len(parts) != 2:
                print("File name is likely not valid as splitting on '.' yielded {} parts instead of 2".format(len(parts)))
                raise IndexError
            else:
                self.is_stream = False
                self.file_name = parts[0]
                self.file_type = parts[1]
        else:
            self.is_stream = True
            self.file_name = None
            self.file_type = None

    def parse_out_type(self, out_type):
        default = 'mid'
        out_types = ['mid', 'wav', 'flac', 'mp3', 'ogg', 'flv', 'mp4', 'wma', 'aac']

        if type(out_type) == int:
            if out_type >= len(out_types):
                print('Index out of range. Defaulting to MIDI')
                return default
            else:
                return out_types[out_type]

        if type(out_type) != str:
            print("Invalid input type. Expected 'str' or 'int', got '{}' instead.".format(type(out_type)))
            print('Defaulting to MIDI')
            return default
        else:
            if out_type.lower() not in out_types:
                if not (out_type.lower() == 'midi'):
                    print('Unsupported file type. Defaulting to MIDI')
                return default
            else:
                return out_type

    def save_song_from_file(self):
        if self.tune[-3:] == 'mid':
            # TODO - Enable saving from MIDI directly
            print('MIDI not able to be loaded from currently. Saving to WAV as failsafe.')
            fs = FluidSynth()
            fs.midi_to_audio(default+self.tune, default+self.file_name+'.wav')
        else:
            with open(default+self.tune, "rb") as audio:
                audio_segment = AudioSegment.from_file(audio, format=self.file_type)
                audio_segment.export(default + self.file_name + '.' + self.out_type, format=self.out_type)

        """
        if self.file_type == 'mid':
            fs = FluidSynth()
            # TODO
            fs.midi_to_audio('input.mid', 'output.wav')
        elif self.file_type == 'flac':
            pass
        elif self.file_type == 'wav':
            audio = AudioSegment.from_wav(self.tune)
        elif self.file_type == 'mp3':
            audio = AudioSegment.from_mp3(self.tune)
        elif self.file_type == 'ogg':
            audio = AudioSegment.from_ogg(self.tune)
        elif self.file_type == 'flv':
            audio = AudioSegment.from_flv(self.tune)
        else:
            audio = AudioSegment.from_file(self.tune, self.file_type)
        """

    def save_song_from_stream(self):
        # TODO - Use python temp file to save to MIDI
        self.tune.write('midi', fp=default + 'song_{}.{}'.format(self.num, self.file_type))

    def stream_to_midi(self):
        self.tune.write('midi', fp=default + 'song_{}.mid'.format(self.num))

    def save_song(self):
        if self.is_stream:
            self.save_song_from_stream()
        self.save_song_from_file()


if __name__ == '__main__':
    conv = Converter('song_0.wav', out_type='mp3')
    conv.save_song_from_file()


"""
# using the default sound font in 44100 Hz sample rate
fs = FluidSynth()
fs.midi_to_audio('input.mid', 'output.wav')
fs.midi_to_audio('input.mid', 'output.flac')

wav_version = AudioSegment.from_wav("never_gonna_give_you_up.wav")
mp3_version = AudioSegment.from_mp3("never_gonna_give_you_up.mp3")
ogg_version = AudioSegment.from_ogg("never_gonna_give_you_up.ogg")
flv_version = AudioSegment.from_flv("never_gonna_give_you_up.flv")

mp4_version = AudioSegment.from_file("never_gonna_give_you_up.mp4", "mp4")
wma_version = AudioSegment.from_file("never_gonna_give_you_up.wma", "wma")
aac_version = AudioSegment.from_file("never_gonna_give_you_up.aiff", "aac")

awesome.export("mashup.mp3", format="mp3")
"""