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
    :return: A sorted list of relevant tun dictionaries.
    """
    cleaned = list()
    for t in tunes:

        if types and t['type'] not in types: continue
        if meters and t['meter'] not in meters: continue
        if modes and t['mode'] not in modes: continue

        tune = dict()
        cats = ["tune", "setting", "type", "meter", "mode"]
        for c in cats: tune[c] = t[c]
        tune['abc'] = Clean.clean(t['abc'], tune['setting'])
        if tune['abc'] != '!!BAD ABC!!':
            cleaned.append(tune)

    print(len(cleaned))
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


def list_to_dict(lst):
    """
    Takes a list of dicts, and returns a dict of dicts.
    """
    tunes = dict()
    for x in lst:
        tunes[x['setting']] = x
    return tunes


def raw_to_dict(fname, default_folder='../Tunes/', types=None, meters=None, modes=None, update=False):
    """
    :param fname: Name of the file for the dict. Ex: 'Tunes.py'
    If given None, it will print the stats to screen.
    :param types: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param meters: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param modes: A list of strings which is checked against the appropriate dict key.
    Skips parsing the tune if it doesn't fit the parameters.
    :param default_folder: Optional path of a folder that the files should be saved in.
    Default is: '../Tunes/'
    :param update: Flag to update the raw data from the Session's Github page.
    :return:
    """
    from Tunes import Tunes_raw as raw
    from PreProcessing import Generate_Stats
    # If the update flag is set, retrieve the new data from the Session.
    if update: update_tunes()

    # Sort the tunes and hand it to the cleaning function.
    tunes = sorted(raw.tunes, key=lambda x: int(x['setting']), reverse=True)
    clean = create_dict_list(tunes, types=types, meters=meters, modes=modes)

    # Generate the stats of the cleaned tunes and save them. Has a small check to prevent a file-out error.
    Generate_Stats.parse_stats(clean, default_folder + '/' + fname + '_Stats.txt')
    dicts_to_file(clean, default_folder + '/' + fname + '.py')
    return list_to_dict(clean)


def simple_clean():
    raw_to_dict('Tunes_cleaned.py')


def jigs_and_reels():
    raw_to_dict('Tunes_JR.py', types=['jig', 'reel'])


def common_time_clean():
    raw_to_dict('Common_Time.py', meters=['4/4'])


if __name__ == '__main__':
    common_time_clean()
