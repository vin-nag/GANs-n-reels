from PreProcessing import Cleaner as Clean
from datetime import datetime


def create_dict(tunes, types=None, meters=None, modes=None, check_abc=True):
    cats = ["tune", "setting", "type", "meter", "mode"]
    cleaned = dict()
    for t in tunes:

        if types and t['type'] not in types: continue
        if meters and t['meter'] not in meters: continue
        if modes and t['mode'] not in modes: continue

        abc = Clean.remove_whitespace(t['abc'])

        if check_abc:
            safe = Clean.safe_abc(abc)
        else:
            safe = True

        if safe:
            tune = dict()
            for c in cats: tune[c] = t[c]
            tune['abc'] = Clean.remove_repeats(abc, tune['setting'])
            cleaned[t['setting']] = tune

    return cleaned


def dict_to_file(cleaned, fname):
    with open(fname, 'w') as f:
        f.write("created = '" + str(datetime.now()) + "'\n\n")
        f.write("tunes = {\n")
        while True:
            tune = cleaned.pop()
            f.write(tune['setting'] + " : " + str(tune))
            if len(cleaned) == 0: break
            f.write(",\n")
        f.write("\n}")


def master_clean(py_out, stats_out=None, types=None, meters=None, modes=None, check_abc=True, default_folder='Tunes/'):
    from Tunes import Tunes_raw
    from PreProcessing import Generate_Stats
    tunes = Tunes_raw.tunes
    clean = create_dict(tunes, types=types, meters=meters, modes=modes, check_abc=check_abc)
    lst = [clean[d] for d in clean]
    Generate_Stats.parse_stats(lst, default_folder + stats_out)
    dict_to_file(lst, default_folder + py_out)


def simple_clean():
    master_clean('Tunes_cleaned.py', stats_out='Stats_cleaned.txt', check_abc=False)


def jigs_and_reels():
    master_clean('Tunes_JR.py', stats_out='Stats_JR.txt', types=['jig', 'reel'], check_abc=False)


def common_time_clean():
    master_clean('Common_Time.py', stats_out='Common_Time_Stats.txt', meters=['4/4'], check_abc=False)


if __name__ == '__main__':
    common_time_clean()
