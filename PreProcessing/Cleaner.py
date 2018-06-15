import re

# region CLEAN CHARACTERS


def remove_whitespace(abc):
    """
    Takes an abc string, and strips
    the white space from it.
    """
    abc = ''.join(abc.split())
    abc = abc.replace("\\", "")
    abc = abc.replace("\x14", "")
    return abc


def clean_grammar(abc):
    """
    Cleans the varying user input possibilities into a more
    consistent grammar to help simplify future processing
    """
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
    """

    # Removes any of the instructions between '!' and the old '+'
    abc = re.sub('(!.{1,16}!)|(\+.{1,16}\+)|(\{[\^=_\w,\'/]+?\})|(".*?")', '', abc)
    abc = re.sub('[\.~HLMOPSTuv\*\$J!]', '', abc)

    # Preserve triplets, swap out any other length modifiers, then nuke parenthesis
    abc = re.sub('\(3', 'T', abc)
    abc = re.sub('\([\d]', 'X', abc)
    abc = re.sub('[()]', '', abc)

    return abc


def clean_note_lengths(abc):
    """
    Takes the abc string, and removes swung notes and triplets
    """

    # Removes bad or complex timing information
    abc = re.sub(r'([<>])\1+', r'\1', abc)
    abc = re.sub('<>|><', '', abc)
    abc = abc.replace('//', '/4')
    abc = re.sub('([_=^]*[a-gzA-g][,\']*)/([^\d/])', r'\1/2\2', abc)
    abc = re.sub('([_=^]*[a-gzA-g][,\']*)/([^\d/])', r'\1/2\2', abc)

    def remove_swing(x):
        # If the length is 1 or less, set i to the denominator
        if x.group(2) == '': i = '2'
        elif '/' in x.group(2): i = str(int(x.group(2)[1])*2)
        # Otherwise, fractions aren't required
        else:
            c = int(x.group(2))
            if x.group(3) == '>': return x.group(1) + str(int(c*1.5)) + x.group(4) + str(int(c*0.5))
            else: return x.group(1) + str(int(c*0.5)) + x.group(4) + str(int(c*1.5))

        if x.group(3) == '>': return x.group(1) + '3/' + i + x.group(4) + '1/' + i
        else: return x.group(1) + '1/' + i + x.group(4) + '3/' + i

    # This matches all the equal length swing time notes
    abc = re.sub(r'([_=^]*[a-gzA-G][,\']*)(/?[\d]?)([<>])([_=^]*[a-gzA-G][,\']*)\2', remove_swing, abc)
    if '>' in abc or '<' in abc: return '!!BAD ABC - SWING NOT REMOVED!!'

    def remove_triplet(m):
        s = m.group()
        x = re.findall('([_=^]*[a-gzA-g][,\']*)(/?[\d]?)', s[1:])
        abc = ''
        for i in x:
            if   i[1] == '/4':  abc += i[0] + '1/6'
            elif i[1] == '/2':  abc += i[0] + '1/3'
            elif i[1] == '':    abc += i[0] + '2/3'
            elif i[1] == '2':   abc += i[0] + '4/3'
            elif i[1] == '3':   abc += i[0]
            elif i[1] == '4':   abc += i[0] + '4/3'
            else:               return s
        return abc

    # This matches all the equal length triplets
    if '/3' in abc: return '!!BAD ABC - INVALID TRIPLET (/3)!!'
    abc = re.sub('T([_=^]*[a-gzA-g][,\']*/?[\d]?){3}', remove_triplet, abc)
    if 'T' in abc: return '!!BAD ABC - TRIPLET NOT REMOVED!!'

    return abc


def remove_ties(abc, tune_id):
    # TODO - Remove barlines before parsing
    # Current character set for operational grammar: "^=_ zabcdefgABCDEFG ,' /23468 - |"

    # Regex for pitch half: "([\^=_]?[za-gA-G][,']*)"
    # Regex for length half: "(/?[\d]*)"
    # Regex for full tie: "([\^=_]?[za-gA-G][,']*/?[\d]*-[\^=_]?[za-gA-G][,']*/?[\d]*)"
    chars = '^=_zabcdefgABCDEFG,\''

    # Remove ties that are mutli-character
    abc = re.sub('--+', '-', abc)
    if abc[-1] == '-': return '!!BAD ABC - UNFINISHED TIE!!'
    count = abc.count('-')
    for x in range(count):
        i = abc.find('-')
        end_i = i + 1
        start_i = i - 1

        # Check that the tie isn't connected to a barline,
        # and if it's note save the pitch
        note2 = abc[end_i]
        if note2 not in chars or abc[start_i] == '|': continue

        # Increment the end index until we hit the next note.
        while end_i + 1 < len(abc) and abc[end_i + 1] not in chars and abc[end_i + 1] not in '|-': end_i += 1
        end_i += 1
        # Decrement the start index until we hit a pitch, then save it.
        while start_i > 0 and abc[start_i] not in chars: start_i -= 1
        note1 = abc[start_i]

        if note1 != note2:
            # If the two pitches differ, the tie is used as a slur, and is removed.
            abc = abc[:i] + abc[i+1:]
        else:
            # Otherwise, consolidate the notes.
            start = abc[start_i:i]
            end = abc[i + 1:end_i]

            if start == end:
                if len(start) == 1: abc = abc[:start_i] + start + '2' + abc[end_i:]
                elif len(start) == 2:
                    if start[1] == '/': abc = abc[:start_i] + start + abc[end_i:]
                    elif start[1].isdigit(): abc = abc[:start_i] + start[0] + str(int(start[1])*2) + abc[end_i:]
                    elif start[1] in '\',': abc = abc[:start_i] + start + '2' + abc[end_i:]
                    else: print('len(2) unknown: ' + start); return '!!BAD ABC - Unknown Parse Branch'
                elif len(start) == 3:
                    if start[1] == '/':
                        if start[2] == '2': abc = abc[:start_i] + start[0] + abc[end_i:]
                        else: abc = abc[:start_i] + start[0] + str(int(start[1])/2) + abc[end_i:]
                    else: print('len(3) unknown: ' + start); return '!!BAD ABC - Unknown Parse Branch'
                else: print('start == end unkown: ' + start); return '!!BAD ABC - Unknown Parse Branch'
            else:
                if (start[-1] == '/' and start[-2].isdigit()) or (end[-1] == '/' and end[-2].isdigit()):
                    return '!!BAD ABC - Invalid Timing info!!'
                else:
                    print(start)
                    print(end)
                    print()

    return abc
# endregion

# region REMOVE REPEATS
# region 1ST and 2ND REPEATS


def remove_single_dual_repeat(abc, tune_id):
    """
    Takes an abc string, and the tune_id for
    error messages, then removes a single 1st/2nd
    ending. If there are multiple repeats, it calls
    another function to separate the string.
    """

    # Split on the second ending, and check to make sure there are two parts.
    temp = abc.split(':|2')
    end2 = temp.pop()
    if len(temp) == 0: return '!!BAD ABC - BLANK END2!!'

    # Take the first part, and remove the starting repeat if needed, then count the repeats
    x = temp[0]
    if x[:2] == '|:': x = x[2:]
    lrpt = x.count('|:')
    rrpt = x.count(':|')
    cleaned = ''

    # If there are no repeats, it's of form ABAC
    if lrpt == 0 and rrpt == 0:
        beg, end1 = x.split('|1')
        cleaned = beg + '|' + end1 + '|' + beg + '|' + end2 + '|'
        cleaned = remove_repeats(cleaned, tune_id)

    # Otherwise, since there's only simple repeats in the piece,
    # split at the last '|:', parsing the first using
    else:
        simple, ends = x.rsplit('|:', 1)
        beg, end1 = ends.split('|1')
        cleaned = remove_simple_repeats(simple, tune_id) + '|' + beg + '|' + end1 + '|' + beg + '|' + end2 + '|'

    if ':|' in cleaned or '|:' in cleaned:
        return '!!BAD ABC - VALUE ERROR - SIMPLE!!'
    return cleaned


def remove_dual_repeat(abc, tune_id):
    """
    Takes the string, and splits into pieces, specifically
    the beginning 1st ending and 2nd ending, then reconstructs
    it explicitly without the repeats, and returns the string.
    """
    if len(abc) == 0:
        return ''
    elif abc[0] == '1' or abc[0] == ':':
        return '!!BAD ABC - MALFORM STRING!!'

    cleaned = ''
    count1 = abc.count('|1')
    count2 = abc.count(':|2')

    # If the number of 1st and 2nd endings are the same,
    # we can somewhat safely assume that the structure is sound
    if count1 == count2:
        temp = abc.split(':|2')
        end = temp.pop()
        good_str = True
        for x in temp: good_str = good_str and ('|1' in x)

        if good_str:
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
        else:
            return '!!BAD ABC - MISMATCH ENDS!!'
    # Otherwise, something is very wrong
    elif count1 > count2:
        # TODO - 140? 100?
        #print(abc)
        return '!!BAD ABC - END1!!'
    elif count2 > count1:
        # TODO
        #print(abc)
        return '!!BAD ABC - END2!!'
    return cleaned
# endregion
# region SIMPLE REPEATS


def remove_simple_repeats(abc, tune_id):
    """
    Takes a string, which only has simple repeats in it and
    returns a string with the repeats explicitly written.
    """
    cleaned = ''

    if abc.count(':|') > abc.count('|:'):
        temp = abc.split(':|')
        end = temp.pop()
        if '|:' in end:
            end = remove_simple_repeats(end, tune_id)
        for x in temp:
            if '|:' in x:
                cleaned += remove_simple_repeats(x, tune_id) + '|'
            else:
                cleaned += x + '|' + x + '|'
        cleaned += end + '|'

    elif abc.count(':|') <= abc.count('|:'):
        temp = abc.split('|:')
        beg = temp.pop(0)
        if ':|' in beg:
            cleaned = remove_simple_repeats(beg, tune_id)
        else:
            cleaned = beg + '|'
        for x in temp:
            if ':|' in x:
                cleaned += remove_simple_repeats(x, tune_id)
            else:
                cleaned += x + '|' + x + '|'
    return cleaned
# endregion
# endregion

# region MAIN


def print_bad_abc(abc, tune_id, extra=list()):
    """
    :param abc: A valid abc string
    :param tune_id: The setting of the tune, as it is unique
    :param extra: A list of strings which is optional, it prints them as extra
    :return: None
    """
    print()
    print('BAD ABC:  Tune-' + str(tune_id) + '   ', end='')
    if 'K:' in abc:
        print('Extra Key Information')
    else:
        print()
    print(abc)
    for x in extra: print(x)
    print()


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

    while ']' in cleaned: cleaned = cleaned.replace(']', '|')
    while '||' in cleaned: cleaned = cleaned.replace('||', '|')
    if cleaned[0] == '|': cleaned = cleaned[1:]

    return cleaned


def remove_bad_tunes(abc):
    """
     Checks if the song has qualities which make it unusable.
    """

    # Removes any songs less than X+1 bars long.
    if abc.count('|') < 15:
        return '!!BAD ABC - SHORT PIECE'

    # Removes and song which has characters not contained in the defined grammar
    chars = set(x for x in "zabcdefgABCDEFG23468T-^=_,></'|")
    tune = set(x for x in abc)
    if len(tune - chars) != 0:
        return '!!BAD ABC - INVALID CHARS!!'

    return abc


def clean(abc, tune_id):
    """
    :param abc: An abc string
    :param tune_id: The tune setting
    :return: Either '!!BAD ABC!!' or a valid abc string
    """
    abc = remove_whitespace(abc)
    abc = clean_grammar(abc)
    abc = remove_ornaments(abc)
    cleaned = remove_repeats(abc, tune_id)
    cleaned = remove_bad_tunes(cleaned)
    cleaned = clean_note_lengths(cleaned)
    # if '-' in cleaned: cleaned = remove_ties(cleaned, tune_id)

    if '!!BAD ABC' in cleaned:
        # print_bad_abc(abc, tune_id)
        return '!!BAD ABC!!'
    return cleaned
# endregion
