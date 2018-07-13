from src.Generation import Cleaner as Clean
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
            with open('../../Data/Raw/The_Session_Raw.py', 'w') as f:
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
    tunes = sorted(tunes, key=lambda x: int(x['setting']), reverse=True)
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

    print('{}/{} tunes successfully cleaned!'.format(len(cleaned), len(tunes)))
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

