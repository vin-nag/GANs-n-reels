import re

MIN_BARS = 15
GRAMMAR_CHARACTERS = "zabcdefgABCDEFG23468T-^=_,></'|"

# region REGULAR EXPRESSION OBJECTS
# region --- Grammar Cleaning
APOSTROPHE_RE = re.compile('[’`´]')
SEMICOLON_RE = re.compile(';')
BARLINES_RE = re.compile('(\|]+)|(\[+\|)|(\|!\|)')
REPEATS_RE = re.compile(':\|*:+')
END_1_RE = re.compile('(\|*\[?1\.?)')
END_2_RE = re.compile('(:?\|+\[?2\.?)|(:\|1)')
QUIRK_1_RE = re.compile('--+')
QUIRK_2_RE = re.compile(r'([<>])\1+')
QUIRK_3_RE = re.compile('<>|><')
# endregion --- Grammar Cleaning

# region --- Ornamentation Cleaning
COMMENTS_RE = re.compile('(!.{1,16}!)|(\+.{1,16}\+)|({[\^=_\w,\'/]+?\})|(".*?")')
ORNAMNETS_RE = re.compile('[.~HLMOPSTuv*$J!]')
FIND_TRIPLETS_RE = re.compile('\(3')
TUPLES_RE = re.compile('\([\d]')
SLURS_RE = re.compile('[()]')
# endregion --- Ornamentation Cleaning

# region --- Timing Cleaning
SWUNG_NOTES_RE = re.compile(r'([_=^]*[a-gzA-G][,\']*)(/?[\d]?)([<>])([_=^]*[a-gzA-G][,\']*)\2')
TIES_RE = re.compile('([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)-([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)')
OLD_NOTE_RE = re.compile('([_=^]*[a-gzA-g][,\']*)(/?[\d]?)')
REPLACE_TRIPLETS_RE = re.compile('T([_=^]*[a-gzA-g][,\']*/?[\d]?){3}')
IMPLIED_HALF_LENGTH_RE = re.compile('([_=^]*[a-gzA-g][,\']*)/([^\d])')
# endregion --- Timing Cleaning

# region --- Fraction Handling
ISOLATE_TIME_RE = re.compile('[_=^]*[a-gzA-G][,\']*([\d]*/?[\d]*)')
FRACTIONAL_PARTS_RE = re.compile('([\d]*)/?([\d]*)')
# endregion --- Fraction Handling

HANDLE_ACCIDENTALS_RE = re.compile('[_=^]+[a-gzA-G][,\']*')

# endregion REGULAR EXPRESSION OBJECTS


# region CLEAN CHARACTERS
def clean_grammar(abc):
    """
    Cleans the varying user input possibilities into a more
    consistent grammar to help simplify future processing
    """
    abc = ''.join(abc.split())
    abc = abc.replace("\\", "")
    abc = abc.replace("\x14", "")

    # Replaces mistyped repeats and apostrophes
    abc = SEMICOLON_RE.sub(':', abc)
    abc = APOSTROPHE_RE.sub('\'', abc)

    # Handles extra data in the abc string
    if 'M:' in abc: return '!!BAD ABC - EXTRA TIME SIGNATURE!!'
    if abc[:2] == 'C:' or abc[:2] == 'R:':
        abc = abc[abc.index('|'):]

    # Replaces alternate barline notations
    abc = BARLINES_RE.sub('||', abc)

    # Consolidates repeat grammar
    if abc[0] == ':': abc = '|' + abc
    if abc[-1] == ':': abc = abc + '|'
    abc = REPEATS_RE.sub(':||:', abc)
    abc = END_1_RE.sub('|1', abc)
    abc = END_2_RE.sub(':|2', abc)

    # Fixes other grammatical quirks
    abc = QUIRK_1_RE.sub('-', abc)
    abc = QUIRK_2_RE.sub(r'\1', abc)
    abc = QUIRK_3_RE.sub('', abc)

    return abc


def remove_ornaments(abc):
    """
    Removes ornamentation from the abc string, as
    well as converting triplets and other non base-two
    timing into other characters
    """
    """
        Ornamentation represents trills or other performance enhancers
        See http://abcnotation.com/wiki/abc:standard:v2.1#decorations
        .            staccato mark
        ~            Irish roll
        H            fermata
        L            accent or emphasis
        M            lowermordent
        O            coda
        P            uppermordent
        S            segno
        T            trill
        u            up-bow
        v            down-bow
        *            ???
        $            ???
        J            ???
        
        !***!        Comment or direction
        +***+        Comment or direction
        {***}        Grace note(s)
        "***"        Comments or chord
    """

    # Removes any of the instructions between '!' and the old '+', grace notes and comments
    abc = COMMENTS_RE.sub('', abc)
    abc = ORNAMNETS_RE.sub('', abc)

    # Preserve triplets, swap out any other length modifiers, then nuke parenthesis
    abc = FIND_TRIPLETS_RE.sub('T', abc)
    abc = TUPLES_RE.sub('X', abc)
    abc = SLURS_RE.sub('', abc)

    return abc
# endregion CLEAN CHARACTERS


# region NOTE LENGTHS
def merge_note_lengths(a, b):
    """
    Takes two note lengths parts and returns a string of their sum
    """
    a = FRACTIONAL_PARTS_RE.findall(a)[0]
    b = FRACTIONAL_PARTS_RE.findall(b)[0]
    num, den = simplify_fractions(a, b)
    if num == 1 and den == 1:
        return ''
    elif den == 1:
        return str(num)
    else:
        return str(num) + '/' + str(den)


def simplify_fractions(a, b):
    """
    Takes two tuples which each contain two integer convertable values,
    and returns a simplified fraction as a tuple.
    :param a: A tuple in the form (numerator, denominator)
    :param b: A tuple in the form (numerator, denominator)
    :return: A simplified tuple of ints in the form (numerator, denominator)
    """
    num1 = int(a[0]) if a[0] != '' else 1
    num2 = int(b[0]) if b[0] != '' else 1
    den1 = int(a[1]) if a[1] != '' else 1
    den2 = int(b[1]) if b[1] != '' else 1
    den = den1 * den2

    # Both denominators are 1, sum the numerators
    if den == 1:
        num = num1 + num2
    else:
        # Cross multiply
        num = (num1 * den2) + (num2 * den1)
        c = 2
        # And remove common factors
        while den != 1 and num != 1 and c <= den and c <= num:
            while den % c == 0 and num % c == 0:
                den = den // c
                num = num // c
            c += 1
    return num, den


def count_bar(bar):
    time = ISOLATE_TIME_RE.findall(bar)

    num_sum = 0
    den_sum = 1
    for x in time:
        a = FRACTIONAL_PARTS_RE.findall(x)[0]
        num_sum, den_sum = simplify_fractions(a, (num_sum, den_sum))

    return num_sum / den_sum


def remove_swing_notes(abc):

    def remove_swing_helper(x):
        a = FRACTIONAL_PARTS_RE.findall(x.group(2))[0]
        num = int(a[0]) if a[0] != '' else 1
        den = int(a[1]) if a[1] != '' else 1
        half = str(num) + '/' + str(den*2)
        short = merge_note_lengths(half, '0/1')
        long = merge_note_lengths(half, x.group(2))

        if x.group(3) == '>': return x.group(1) + long + x.group(4) + short
        else: return x.group(1) + short + x.group(4) + long

    # This matches all the equal length swing time notes
    abc = SWUNG_NOTES_RE.sub(remove_swing_helper, abc)
    if '>' in abc or '<' in abc: return '!!BAD ABC - SWING NOT REMOVED!!'
    return abc


def remove_triplets(abc):

    def remove_triplets_helper(m):
        s = m.group()
        x = OLD_NOTE_RE.findall(s[1:])
        abc = ''
        # For all the notes in x, use the current length to determine the new length
        for i in x:
            if   i[1] == '/4':  abc += i[0] + '/6'
            elif i[1] == '/2':  abc += i[0] + '/3'
            elif i[1] == '':    abc += i[0] + '2/3'
            elif i[1] == '2':   abc += i[0] + '4/3'
            elif i[1] == '3':   abc += i[0]
            elif i[1] == '4':   abc += i[0] + '8/3'
            else:               return '!!BAD ABC - TRIPLET TOO SMALL!!'
        return abc

    # This matches all the equal length triplets, then removes grammatically incorrect strings
    if '/3' in abc: return '!!BAD ABC - INVALID TRIPLET (/3)!!'
    abc = REPLACE_TRIPLETS_RE.sub(remove_triplets_helper, abc)
    if 'T' in abc: return '!!BAD ABC - TRIPLET NOT REMOVED!!'
    return abc


def remove_ties(abc):

    def condense_ties(m):
        if m.group(1) != m.group(3):
            # Pitches are different. Remove '-'
            return m.group().replace('-', '')
        else:
            # Pitches are the same. Merge note lengths
            return m.group(1) + merge_note_lengths(m.group(2), m.group(4))

    # TODO - Replace with a single re.sub call
    abc = TIES_RE.sub(condense_ties, abc)
    abc = TIES_RE.sub(condense_ties, abc)
    abc = TIES_RE.sub(condense_ties, abc)

    return abc
# endregion NOTE LENGTHS


# region REMOVE REPEATS
def repair_bars(abc):
    """
    Takes an abc string, and merges pickups and bars which are too short.
    """

    # Split into individual bars, remove the first and last bar
    # as these could be pickup related, and non-standard length
    bars = abc.split('|')
    if len(bars) < 3: return abc
    end = bars.pop()
    if end == '': end = bars.pop()
    cleaned = bars.pop(0) + '|'
    x = 0
    while x < len(bars):
        bar = bars[x]
        s = count_bar(bar)
        if s % BEATS_PER_BAR != 0 and x < len(bars)-1 and (s + count_bar(bars[x+1])) % BEATS_PER_BAR == 0:
            cleaned += bar + bars[x+1] + '|'
            x += 1
        else:
            cleaned += bar + '|'
        x += 1
    cleaned += end + '|'
    return cleaned


def remove_single_dual_repeat(abc, tune_id):
    """
    Takes a string with one 1st and 2nd ending, and removes it
    """

    # Split on the second ending, and check to make sure there are two parts.
    temp = abc.split(':|2')
    end2 = temp.pop()
    if len(temp) == 0: return '!!BAD ABC - BLANK END2!!'

    # Take the first part, and remove the starting repeat if needed, then count the repeats
    x = temp[0]
    cleaned = ''
    if x[:2] == '|:': x = x[2:]

    # If there is more than 1 repeat, isolate the 1st ending, and deal with the other repeats
    if x.count(':|') != 0 or x.count('|:') != 0:
        simple, x = x.rsplit('|:', 1)
        cleaned = remove_simple_repeats(simple, tune_id) + '|'

    # Split on the 1st ending, isolating the part that repeats
    beg, end1 = x.split('|1')
    cleaned += beg + '|' + end1 + '|' + beg + '|' + end2 + '|'

    if ':|' in cleaned or '|:' in cleaned:
        return '!!BAD ABC - VALUE ERROR - SIMPLE!!'
    return cleaned


def remove_dual_repeat(abc, tune_id):
    """
    Takes the string, and splits into pieces, specifically
    the beginning 1st ending and 2nd ending, then reconstructs
    it explicitly without the repeats, and returns the string.
    """

    # If the string is empty, do nothing. If the string starts with 1 or :,
    # it is effectively un-salvageable.
    if len(abc) == 0: return ''
    elif abc[0] == '1' or abc[0] == ':': return '!!BAD ABC - MALFORM STRING!!'

    cleaned = ''
    count1 = abc.count('|1')
    count2 = abc.count(':|2')

    # If the number of 1st and 2nd endings are the same,
    # we can somewhat safely assume that the structure is sound
    if count1 == count2:
        # If a 2nd ending isn't paired with a first ending
        for x in abc.split(':|2')[:-1]:
            if '|1' not in x: return '!!BAD ABC - MISMATCH ENDS!!'

        try:
            for x in range(count1):
                loc1 = abc.index('|1') + 1
                loc2 = abc.index(':|2') + 2
                bars = 0
                fin = loc2

                # TODO - Simplify this using regex.
                # Count the groups of '|' in the ranges of the abc string
                # This approach does assume that the 1st and 2nd ending are
                # of the same bar length, though that's reasonable considering
                # the AABB format of most Irish music.

                while loc1 < loc2:
                    loc1 += 1
                    if abc[loc1] != '|':
                        continue
                    else:
                        while abc[loc1] == '|':
                            loc1 += 1
                        bars += 1

                while bars > 0:
                    fin += 1
                    if fin >= len(abc): break
                    if abc[fin] != '|':
                        continue
                    else:
                        while abc[fin] == '|':
                            fin += 1
                            if fin >= len(abc): break
                        bars -= 1

                sub = abc[:fin-1]
                abc = abc[fin-1:]
                cleaned += remove_single_dual_repeat(sub, tune_id)
        except ValueError:
            return '!!BAD ABC!!'
    # Otherwise, something is very wrong with the endings
    elif count1 > count2: return '!!BAD ABC - TOO MANY END1s!!'
    elif count2 > count1: return '!!BAD ABC - TOO MANY END2s!!'
    else: return '!!BAD ABC - UNKNOWN ENDING!!'
    return cleaned


def remove_simple_repeats(abc, tune_id):
    """
    Takes a string, which only has simple repeats in it and
    returns a string with the repeats explicitly written.
    """
    cleaned = ''

    if abc.count(':|') > abc.count('|:'):
        temp = abc.split(':|')
        # Remove the 'outside' element, as it isn't repeated
        end = temp.pop()
        # Unless it needs to be repeated due to the opposite repeat
        if '|:' in end: end = remove_simple_repeats(end, tune_id)
        for x in temp:
            # Process the chunk if it has the other repeat, otherwise double it
            if '|:' in x: cleaned += remove_simple_repeats(x, tune_id) + '|'
            else: cleaned += x + '|' + x + '|'
        cleaned += end + '|'

    # Follows the above logic, just in reverse
    elif abc.count(':|') <= abc.count('|:'):
        temp = abc.split('|:')
        beg = temp.pop(0)
        if ':|' in beg: cleaned = remove_simple_repeats(beg, tune_id)
        else: cleaned = beg + '|'
        for x in temp:
            if ':|' in x: cleaned += remove_simple_repeats(x, tune_id)
            else: cleaned += x + '|' + x + '|'

    return cleaned
# endregion REMOVE REPEATS


def parse_accidentals(abc):
    cleaned = ''
    bars = abc.split('|')
    for bar in bars:
        accidentals = HANDLE_ACCIDENTALS_RE.findall(bar)

        # There are no accidentals, add the bar and continue
        if len(accidentals) == 0:
            cleaned += bar + '|'

        # Pass over bars which have a single accidental, that comes after all other notes of the same pitch
        elif len(accidentals) == 1 and bar.count(accidentals[0][1:], bar.index(accidentals[0])+len(accidentals[0])) == 0:
            cleaned += bar + '|'

        # If the number of target pitches is the same as the number of accidentals, all of the relevant notes
        # already have accidentals, so the bar is skipped.
        elif sum([bar.count(i) for i in set(accidentals)]) == sum([bar.count(i) for i in set([j[1:] for j in accidentals])]):
            cleaned += bar + '|'

        elif len(accidentals) == 1:
            acc = accidentals[0]
            piv = bar.index(acc) + len(acc)
            cleaned += bar[:piv] + bar[piv:].replace(acc[1:], acc) + '|'

        else:
            # TODO - Handle more complex accidental structures appropriately.
            return '!!BAD ABC - TEMPORARY ACCIDENTAL REMOVAL!!'

    return cleaned


# region MAIN
def remove_repeats(abc, tune_id):
    """
    :param abc: A spaceless abc string
    :param tune_id: The tune setting
    :return: An abc string, without repeats, and single barlines
    """

    # If the song has first or second endings, we need to remove those first
    if '|1' in abc or ':|2' in abc:
        cleaned = remove_dual_repeat(abc, tune_id)
    # Otherwise, if it has repeats, we deal with those
    elif '|:' in abc or ':|' in abc:
        cleaned = remove_simple_repeats(abc, tune_id)
    # If there are no repeats, return the spaceless string
    else:
        cleaned = abc

    # Normalize the barline grammar, for future processing
    while ']' in cleaned: cleaned = cleaned.replace(']', '|')
    while '||' in cleaned: cleaned = cleaned.replace('||', '|')
    if cleaned[0] == '|': cleaned = cleaned[1:]

    # Condense bars which were improperly split
    cleaned = repair_bars(cleaned)

    return cleaned


def remove_bad_tunes(abc):
    """
     Checks if the song has qualities which make it unusable.
    """

    # Removes any songs less than X+1 bars long.
    if abc.count('|') < MIN_BARS:
        return '!!BAD ABC - SHORT PIECE'

    # Removes any song which has characters not contained in the defined grammar
    chars = set(x for x in GRAMMAR_CHARACTERS)
    tune = set(x for x in abc)
    if len(tune - chars) != 0:
        return '!!BAD ABC - INVALID CHARS!!'

    return abc


def clean_note_lengths(abc):
    """
    Takes the abc string, and normalizes the length grammar
    """

    # Makes implicit not lengths explicit
    abc = abc.replace('//', '/4')
    # TODO - Replace with a single re.sub call
    abc = IMPLIED_HALF_LENGTH_RE.sub(r'\1/2\2', abc)
    abc = IMPLIED_HALF_LENGTH_RE.sub(r'\1/2\2', abc)

    abc = remove_swing_notes(abc)
    abc = remove_triplets(abc)

    return abc


def check_time(abc):
    bars = abc.split('|')
    s = 0
    try:
        for bar in bars: s += count_bar(bar)
    except ValueError:
        return '!!BAD ABC - INCORRECT BAR LENGTH!!'
    if s % BEATS_PER_BAR == 0:
        # There is an appropriate number of beats in the whole tune
        pass
        # abc = '!!BAD ABC - INCORRECT BAR LENGTH!!'
    else:
        if (s - count_bar(bars[0])) % BEATS_PER_BAR == 0:
            # The piece has the right number of beats, minus the pickup bar
            # pass
            abc = '!!BAD ABC - INCORRECT BAR LENGTH!!'
        else:
            # There is a non-standard number of beats somwhere other than the pickup
            abc = '!!BAD ABC - INCORRECT BAR LENGTH!!'
    return abc


def print_bad_abc(abc, tune_id, extra=list()):
    """
    :param abc: A valid abc string
    :param tune_id: The setting of the tune, as it is unique
    :param extra: A list of strings which is optional, it prints them as extra
    """
    # TODO - Make more robust
    print()
    print('BAD ABC:  Tune-' + str(tune_id) + '   ', end='')
    if 'K:' in abc:
        print('Extra Key Information')
    else:
        print()
    print(abc)
    for x in extra: print(x)
    print()


def clean(abc, tune_id='Test'):
    """
    :param abc: An abc string
    :param tune_id: The tune setting, which is used as the unique id
    :return: Either '!!BAD ABC!!' or a valid abc string
    """
    global BEATS_PER_BAR, BEAT_SUBDIVISIONS
    # TODO - Base this on time signature
    BEATS_PER_BAR = 4

    # TODO - Base this on the most frequent sum of notes in a bar
    BEAT_SUBDIVISIONS = 1

    abc = clean_grammar(abc)
    abc = remove_ornaments(abc)
    cleaned = remove_repeats(abc, tune_id)
    cleaned = remove_bad_tunes(cleaned)
    cleaned = clean_note_lengths(cleaned)
    cleaned = check_time(cleaned)
    cleaned = parse_accidentals(cleaned)
    if '-' in cleaned: cleaned = remove_ties(cleaned)

    if '!!BAD ABC' in cleaned:
        # print_bad_abc(abc, tune_id)
        return '!!BAD ABC!!'
    return cleaned
# endregion MAIN
