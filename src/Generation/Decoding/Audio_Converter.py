from midi2audio import FluidSynth
from pydub import AudioSegment
import tempfile

# TODO - Determine why MIDI saves correctly, but WAVa nd MP3 do not.

default = '../../Data/Audio/'


class Converter:
    """
    This module requires other audio packages to function:
    Music21
    midi2audio
    FluidSynth
    pydub
    FFmpeg
    """
    def __init__(self, tune, out_type='mid', num=0):
        """
        Given a song and a file type the class will crunch some data,
        and determine the settings to save the input to the output format.

        :param tune: A file name, or a stream object.
        :param out_type: The file type to be saved as.
        :param num: The song number.
        Note: Used only when dealing with generated streams which have no identifier.
        (For our project this is the GAN output.)
        """
        self.out_type = self.parse_out_type(out_type)
        self.tune = tune
        self.num = num

        if type(tune) == str:
            parts = tune.split('.')
            if len(parts) != 2:
                print("Splitting on '.' yielded {} parts instead of 2".format(len(parts)))
                raise IndexError
            else:
                self.is_stream = False
                self.file_name = parts[0]
                self.file_type = parts[1]
        else:
            self.is_stream = True
            self.file_name = None
            self.file_type = None

    def set_out_type(self, out_type):
        self.out_type = self.parse_out_type(out_type)

    def parse_out_type(self, out_type):
        """
        Helper function to ensure the file type is valid/manageable.
        """
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

    def save_song_from_stream(self):
        file_out = default + 'song_{}.{}'.format(self.num, self.out_type)

        if self.out_type == 'mid':
            # Save directly to disk. Music21 automatically handles this
            self.tune.write('midi', fp=file_out)
            return

        # If we get to here, we need to rely on other libraries, so we create
        # so we create the MIDI file as a temp file.
        fs = FluidSynth()
        temp_midi = tempfile.NamedTemporaryFile()
        self.tune.write('midi', fp=temp_midi.name)
        temp_midi.seek(0)
        if self.out_type == 'wav' or self.out_type == 'flac':
            # If wav or flac, we use midi2audio and fluidsynth to save to the format
            # by using the temp MIDI file as input.
            fs.midi_to_audio(temp_midi.name, file_out)
        else:
            # For the other formats, we use pydub and FFmpeg which takes a WAV file,
            # so we use the temp MIDI to create a temp WAV, and convert that.
            temp_wav = tempfile.NamedTemporaryFile()
            fs.midi_to_audio(temp_midi.name, temp_wav.name)
            temp_wav.seek(0)

            with open(temp_wav.name, "rb") as audio:
                # Open the temp WAV file, and save it as the appropriate type.
                audio_segment = AudioSegment.from_file(audio, format='wav')
                audio_segment.export(file_out, format=self.out_type)

        temp_midi.close()

    def save_song_from_file(self):
        file_in = default+self.tune
        file_out = default + '{}.{}'.format(self.file_name, self.out_type)

        # If the input is MIDI, we need to use a temporary file to convert to WAV.
        if self.tune[-3:] == 'mid':
            fs = FluidSynth()
            temp_wav = tempfile.NamedTemporaryFile()
            fs.midi_to_audio(file_in, temp_wav.name)
            temp_wav.seek(0)
            file_in = temp_wav.name

        # Convert and save the file.
        with open(file_in, "rb") as audio:
            audio_segment = AudioSegment.from_file(audio, format=self.file_type)
            audio_segment.export(file_out, format=self.out_type)

    def stream_to_midi(self):
        """
        Quick and dirty save for streams.
        """
        if self.is_stream: self.tune.write('midi', fp=default + 'song_{}.mid'.format(self.num))
        else: print('ERROR! Song is a file name, not a stream.')

    def save_song(self):
        """
        Saves the song based on whether it is a file name or stream.
        """
        if self.is_stream:
            self.save_song_from_stream()
        else:
            self.save_song_from_file()


if __name__ == '__main__':
    conv = Converter('song_0.wav', out_type='mp3')
    conv.save_song()
