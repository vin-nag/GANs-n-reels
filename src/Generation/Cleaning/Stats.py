from datetime import datetime
import numpy as np
import importlib.util as ih

FOLDER_NAME = '../../Data'
ABC_DIR = '/Clean/'
STATS_DIR = '/Statistics/'
NPY_DIR = '/Vectors/'


class StatsHandler:
    def __init__(self, filename, base_key='Cmaj'):
        self.filename = filename
        self.base_key = base_key

        self.notes_in_key = [60, 62, 64, 65, 67, 69, 71, 72]
        self.abc_tunes = self.read_dict_file()
        self.vec_tunes = self.read_npy_file()
        self.stats = StatsObject(self.abc_tunes, self.vec_tunes)

    def read_dict_file(self):
        try:
            spec = ih.spec_from_file_location("tunes", FOLDER_NAME + ABC_DIR + self.filename + ".py")
            foo = ih.module_from_spec(spec)
            spec.loader.exec_module(foo)
            tunes = foo.tunes
        except FileNotFoundError:
            print('Python file not found!')
            tunes = []
        return tunes

    def read_npy_file(self):
        fname = FOLDER_NAME + NPY_DIR + self.filename + '_Notes.npy'
        try:
            array = np.load(fname)
        except FileNotFoundError:
            print('Numpy file not found!')
            array = []
        return array

    def reread_files(self):
        self.abc_tunes = self.read_dict_file()
        self.vec_tunes = self.read_npy_file()

    def save_stats_to_file(self):
        self.stats.save_stats(self.filename)


class StatsObject:
    def __init__(self, abc_tunes, vec_tunes):
        self.vec_tunes = vec_tunes
        self.total_tunes = 0
        self.tune_styles = dict()
        self.tune_meters = dict()
        self.tune_modes = dict()
        self.mode_types_fine = dict()
        self.mode_types_coarse = dict()
        self.parse_abc_tunes(abc_tunes)

    def parse_abc_tunes(self, tunes):
        def inc(key, master):
            if key in master:
                master[key] += 1
            else:
                master[key] = 1

        for t in tunes:
            t = tunes[t]
            inc(t['type'], self.tune_styles)
            inc(t['meter'], self.tune_meters)
            inc(t['mode'], self.tune_modes)
            self.total_tunes += 1

        for x in self.tune_modes:
            s = str(x)
            X = s[0]
            s = s[1:]
            if s in self.mode_types_fine:
                self.mode_types_fine[s].append(X)
                self.mode_types_coarse[s] += self.tune_modes[x]
            else:
                self.mode_types_fine[s] = [X]
                self.mode_types_coarse[s] = self.tune_modes[x]

    def save_stats(self, outfile):
        def print_continous_data(d, s=None):
            out = ""
            if s: out += "{} different types of {} were found.\n".format(len(d), s)
            lines = ["{: <14} - {: <5} / {: <5} --> {:8.2f}%".format(x, d[x], self.total_tunes, (100 * d[x] / self.total_tunes)) for x in d]
            out += '\n'.join(sorted(lines)) + "\n\n"
            return out

        def print_discrete_data(d, s=None):
            out = ""
            if s: out += "{} different types of {} were found.\n".format(len(d), s)
            lines = ["{: <14} - {}".format(x, d[x]) for x in d]
            out += '\n'.join(sorted(lines)) + "\n\n"
            return out

        out = "\n" + str(datetime.now()) + "\n\n"
        out += 'A total of {} tunes were scanned.\n'.format(self.total_tunes)
        out += print_continous_data(self.tune_styles, "SONG STYLES")
        out += print_continous_data(self.tune_meters, "TIME SIGNATURES")
        out += print_continous_data(self.tune_modes, "KEY SIGNATURES")
        out += print_discrete_data(self.mode_types_fine, "MODE TYPES")
        out += print_continous_data(self.mode_types_coarse)

        with open(FOLDER_NAME + STATS_DIR + outfile + '.txt', 'w') as f: f.write(out)


if __name__ == '__main__':
    # from Data.Raw.The_Session_Raw import tunes
    # parse_stats(tunes, '../../Data/Statistics/The_Session_Raw.txt')
    stats = StatsHandler('Common_Time', 'Cmaj')
    stats.save_stats_to_file()
