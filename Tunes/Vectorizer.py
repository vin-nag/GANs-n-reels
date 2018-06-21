"""
Vectorizer converts cleaned ABC notation into explicit subdivisions of time
"""

BAR_SUBDIVISION = 48

def vectorize_frame(df):
    """
    Takes a pandas dataframe and returns it with 2 new frames appended for notes and timing
    :param df: pandas dataframe with an 'abc' column
    :return: a copy of the frame with the new columns appended
    """
    pass

def split_by_bar(abc_string):
    """
    Takes a string of full ABC notation and splits it into lists representing individual bars
    """
    result = abc_string.split('|')
    return [x for x in result if x != '']


def vectorize_bar(abc_string):
    """
    Takes an ABC string of an individual bar and returns that same bar but with 48 notes
    returns the the string of notes as well as a 'timing vector'
    """
    note_out = ""
    time_out = []
    notes_re = re.compile('([_=^]*[a-gzA-G][,\']*)([\d]*)/?([\d]*)')
    notes = notes_re.findall(abc_string)
    for note, num, denom in notes:
        if num == '':
            num = 1
        else:
            num = int(num)
        if denom == '':
            denom = 1
        else:
            denom = int(denom)
        if NOTE_MULT * num / denom % 1 != 0:
            raise Exception(
                "{}*{}/{} is not an integer. Your note multiplier is insufficient".format(NOTE_MULT, num, denom))
        reps = ((NOTE_MULT * num) // denom)
        note_out += note * reps
        note_to_number(note)
        time = np.zeros(reps, dtype=int)
        time[0] = 1
        time_out.append(time)

    return note_out, np.concatenate(time_out)