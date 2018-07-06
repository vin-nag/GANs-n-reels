import re

MIN_BAR_LENGTH = 15
GRAMMAR_CHARACTERS = "zabcdefgABCDEFG23468T-^=_,></'|"

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
    abc = abc.replace(';', ':')
    abc = re.sub('[’`´]', '\'', abc)

    # Handles extra data in the abc string
    if 'M:' in abc: return '!!BAD ABC - EXTRA TIME SIGNATURE!!'
    if abc[:2] == 'C:' or abc[:2] == 'R:':
        abc = abc[abc.index('|'):]

    # Replaces alternate barline notations
    abc = re.sub('(\|]+)|(\[+\|)|(\|!\|)', '||', abc)

    # Consolidates repeat grammar
    if abc[0] == ':': abc = '|' + abc
    if abc[-1] == ':': abc = abc + '|'
    abc = re.sub(':\|*:+', ':||:', abc)
    abc = re.sub('(\|*\[?1\.?)', '|1', abc)
    abc = re.sub('(:?\|+\[?2\.?)|(:\|1)', ':|2', abc)

    # Fixes other grammatical quirks
    abc = re.sub('--+', '-', abc)
    abc = re.sub(r'([<>])\1+', r'\1', abc)
    abc = re.sub('<>|><', '', abc)

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
    abc = re.sub('(!.{1,16}!)|(\+.{1,16}\+)|(\{[\^=_\w,\'/]+?\})|(".*?")', '', abc)
    abc = re.sub('[\.~HLMOPSTuv\*\$J!]', '', abc)

    # Preserve triplets, swap out any other length modifiers, then nuke parenthesis
    abc = re.sub('\(3', 'T', abc)
    abc = re.sub('\([\d]', 'X', abc)
    abc = re.sub('[()]', '', abc)

    return abc
# endregion


# region NOTE LENGTHS


def merge_note_lengths(a, b):
    """
    Takes two note lengths parts and returns a string of their sum
    """
    a = re.findall('([\d]*)/?([\d]*)', a)[0]
    b = re.findall('([\d]*)/?([\d]*)', b)[0]
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


def remove_swing_notes(abc):

    def remove_swing_helper(x):
        a = re.findall('([\d]*)/?([\d]*)', x.group(2))[0]
        num = int(a[0]) if a[0] != '' else 1
        den = int(a[1]) if a[1] != '' else 1
        half = str(num) + '/' + str(den*2)
        short = merge_note_lengths(half, '0/1')
        long = merge_note_lengths(half, x.group(2))

        if x.group(3) == '>': return x.group(1) + long + x.group(4) + short
        else: return x.group(1) + short + x.group(4) + long

    # This matches all the equal length swing time notes
    abc = re.sub(r'([_=^]*[a-gzA-G][,\']*)(/?[\d]?)([<>])([_=^]*[a-gzA-G][,\']*)\2', remove_swing_helper, abc)
    if '>' in abc or '<' in abc: return '!!BAD ABC - SWING NOT REMOVED!!'
    return abc


def remove_triplets(abc):

    def remove_triplets_helper(m):
        s = m.group()
        x = re.findall('([_=^]*[a-gzA-g][,\']*)(/?[\d]?)', s[1:])
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
    abc = re.sub('T([_=^]*[a-gzA-g][,\']*/?[\d]?){3}', remove_triplets_helper, abc)
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
    abc = re.sub('([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)-([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)', condense_ties, abc)
    abc = re.sub('([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)-([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)', condense_ties, abc)
    abc = re.sub('([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)-([_=^]*[a-gzA-G][,\']*)([\d]*/?[\d]*)', condense_ties, abc)

    return abc
# endregion


# region REMOVE REPEATS


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
# endregion


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

    # Finally, normalize the barline grammar, for future checking
    while ']' in cleaned: cleaned = cleaned.replace(']', '|')
    while '||' in cleaned: cleaned = cleaned.replace('||', '|')
    if cleaned[0] == '|': cleaned = cleaned[1:]

    return cleaned


def remove_bad_tunes(abc):
    """
     Checks if the song has qualities which make it unusable.
    """

    # Removes any songs less than X+1 bars long.
    if abc.count('|') < MIN_BAR_LENGTH:
        return '!!BAD ABC - SHORT PIECE'

    # Removes and song which has characters not contained in the defined grammar
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
    abc = re.sub('([_=^]*[a-gzA-g][,\']*)/([^\d/])', r'\1/2\2', abc)
    abc = re.sub('([_=^]*[a-gzA-g][,\']*)/([^\d/])', r'\1/2\2', abc)

    abc = remove_swing_notes(abc)
    abc = remove_triplets(abc)

    return abc


def check_time(abc):

    def count_bar(bar):
        time = re.findall('[_=^]*[a-gzA-G][,\']*([\d]*/?[\d]*)', bar)

        num_sum = 0
        den_sum = 1
        for x in time:
            a = re.findall('([\d]*)/?([\d]*)', x)[0]
            num_sum, den_sum = simplify_fractions(a, (num_sum, den_sum))

        return num_sum / den_sum

    bars = abc.split('|')
    s = 0
    try:
        for bar in bars: s += count_bar(bar)
    except ValueError:
        return '!!BAD ABC - INCORRECT BAR LENGTH!!'
    if s % 4 == 0:
        # There is an appropriate number of beats in the whole tune
        pass
    else:
        if (s - count_bar(bars[0])) % 4 == 0:
            # The piece has the right number of beats, minus the pickup bar
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
    abc = clean_grammar(abc)
    abc = remove_ornaments(abc)
    cleaned = remove_repeats(abc, tune_id)
    cleaned = remove_bad_tunes(cleaned)
    cleaned = clean_note_lengths(cleaned)
    cleaned = check_time(cleaned)
    if '-' in cleaned: cleaned = remove_ties(cleaned)

    if '!!BAD ABC' in cleaned:
        # print_bad_abc(abc, tune_id)
        return '!!BAD ABC!!'
    return cleaned
# endregion
