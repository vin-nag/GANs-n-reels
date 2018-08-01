from midi2audio import FluidSynth
from pydub import AudioSegment
import tempfile

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
        # ['mid', 'wav', 'flac', 'mp3', 'ogg', 'flv', 'mp4', 'wma', 'aac']

        file_out = default + 'song_{}.{}'.format(self.num, self.out_type)

        if self.out_type == 'mid':
            self.tune.write('midi', fp=file_out)
            return

        fs = FluidSynth()
        temp_midi = tempfile.NamedTemporaryFile()
        self.tune.write('midi', fp=temp_midi.name)
        temp_midi.seek(0)
        if self.out_type == 'wav' or self.out_type == 'flac':
            fs.midi_to_audio(temp_midi.name, file_out)
        else:
            temp_wav = tempfile.NamedTemporaryFile()
            fs.midi_to_audio(temp_midi.name, temp_wav.name)
            temp_wav.seek(0)

            with open(temp_wav.name, "rb") as audio:
                audio_segment = AudioSegment.from_file(audio, format='wav')
                audio_segment.export(file_out, format=self.out_type)

        temp_midi.close()

        """
        # create a temporary file and write some data to it
        >> > fp = tempfile.TemporaryFile()
        >> > fp.write(b'Hello world!')
        # read data from file
        >> > fp.seek(0)
        >> > fp.read()
        b'Hello world!'
        # close the file, it will be removed
        >> > fp.close()
        """

    def stream_to_midi(self):
        self.tune.write('midi', fp=default + 'song_{}.mid'.format(self.num))

    def save_song(self):
        if self.is_stream:
            self.save_song_from_stream()
        else:
            self.save_song_from_file()


if __name__ == '__main__':
    conv = Converter('song_0.wav', out_type='mp3')
    conv.save_song_from_file()


"""
# using the default sound font in 44100 Hz sample rate
fs = FluidSynth()
fs.midi_to_audio('input.mid', 'output.wav')
fs.midi_to_audio('input.mid', 'output.flac')

"""