from PreProcessing import Cleaner as Clean
from datetime import datetime
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import ast


def update_tunes():
    """
    Gets the tunes from "The Session"'s Github page, and prints it
    as a python dictionary.
    """
    url = 'https://raw.githubusercontent.com/adactio/TheSession-data/master/json/tunes.json'
    try:
        with closing(get(url, stream=True)) as resp:
            with open('../Tunes/Tunes_raw.py', 'w') as f:
                text = resp.content.decode('utf-8')
                temp = ast.literal_eval(text)

                f.write("created = '" + str(datetime.now()) + "'\n\n")
                f.write("tunes = [\n")
                while True:
                    tune = temp.pop()
                    f.write(str(tune))
                    if len(temp) == 0: break
                    f.write(",\n")
                f.write("\n]")
    except RequestException as e:
        print(e)


def create_dict_list(tunes, types=None, meters=None, modes=None):
    """
    Creates a list of tunes dictionaries, which can be restricted based on style/time.
    :param tunes: List of 'tune' dictionaries.
    :param types: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param meters: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param modes: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param check_abc: If true, omits any tunes which contain characters not found in the
    abc grammar. The check is very aggressive. It may be deprecated, or incoprated into
    the normal filtering in the future.
    :return: A sorted list of relevant tun dictionaries.
    """
    cleaned = list()
    for t in tunes:

        if types and t['type'] not in types: continue
        if meters and t['meter'] not in meters: continue
        if modes and t['mode'] not in modes: continue

        # Make a new dict and save only the useful categories,
        # as well as the cleaned, repeatless abc, and append it
        # to the list
        tune = dict()
        cats = ["tune", "setting", "type", "meter", "mode"]
        for c in cats: tune[c] = t[c]
        tune['abc'] = Clean.clean(t['abc'], tune['setting'])
        if tune['abc'] != '!!BAD ABC!!':
            cleaned.append(tune)

    # Finally, sort the list for human readability.
    return cleaned


def dicts_to_file(cleaned, fname):
    """
    Takes a list of tune dictionaries and prints it to a file,
    as a dictionary using setting as the key.
    :param cleaned: List of tunes dictionaries.
    :param fname: Path to the file to print.
    """
    with open(fname, 'w') as f:
        f.write("created = '" + str(datetime.now()) + "'\n\n")
        f.write("tunes = {\n")
        while True:
            tune = cleaned.pop()
            f.write(tune['setting'] + " : " + str(tune))
            if len(cleaned) == 0: break
            f.write(",\n")
        f.write("\n}")


def master_clean(py_out, stats_out=None, types=None, meters=None, modes=None, default_folder='../Tunes/'):
    """

    :param py_out: Name of the file for the dict. Ex: 'Tunes.py'
    :param stats_out: Name of the for the stats. Ex: 'Stats.txt'
    If given None, it will print the stats to screen.
    :param types: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param meters: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param modes: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param default_folder: Optional path of a folder that the files should be saved in.
    Default is: '../Tunes/'
    :return:
    """
    from Tunes import Tunes_raw as raw
    from PreProcessing import Generate_Stats
    # Sort the tunes and hand it to the cleaning function.
    tunes = sorted(raw.tunes, key=lambda x: int(x['setting']), reverse=True)
    clean = create_dict_list(tunes, types=types, meters=meters, modes=modes)

    # Generate the stats of the cleaned tunes and save them. Has a small check to prevent a file-out error.
    if stats_out:
        Generate_Stats.parse_stats(clean, default_folder + stats_out)
    else:
        Generate_Stats.parse_stats(clean, None)
    dicts_to_file(clean, default_folder + py_out)


def simple_clean():
    master_clean('Tunes_cleaned.py', stats_out='Stats_cleaned.txt')


def jigs_and_reels():
    master_clean('Tunes_JR.py', stats_out='Stats_JR.txt', types=['jig', 'reel'])


def common_time_clean():
    master_clean('Common_Time.py', stats_out='Common_Time_Stats.txt', meters=['4/4'])


if __name__ == '__main__':
    # update_tunes()
    common_time_clean()
