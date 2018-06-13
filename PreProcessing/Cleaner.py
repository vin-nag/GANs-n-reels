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
    Takes barlines and repeats and
    cleans them to a more regular style.
    """
    # Replaces mistyped repeats
    abc = abc.replace(';', ':')
    abc = re.sub('[’`´]', '\'', abc)

    # If the composer data is in the abc string, this
    # trims everything before the first barline.
    if abc[:2] == 'C:' or abc[:2] == 'R:':
        abc = abc[abc.index('|'):]

    # Replacing alternate barline notations, that is:
    # '[|', '|]' and, for whatever reason, '|!|'
    abc = re.sub('(\|]+)|(\[+\|)|(\|!\|)', '||', abc)

    # Fixing malformed repeats at the beginning and end of string
    if abc[0] == ':': abc = '|' + abc
    if abc[-1] == ':': abc = abc + '|'

    # Take any :: shorthand and convert it to ':||:'
    abc = re.sub(':\|*:+', ':||:', abc)

    # Take any permutations 1st and 2nd endings,
    # and consolidate them to a single grammar
    abc = re.sub('(\|*\[?1\.?)', '|1', abc)
    abc = re.sub('(:?\|+\[?2\.?)|(:\|1)', ':|2', abc)

    return abc


def remove_ornaments(abc):
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
    abc = re.sub('[\.~HLMOPSTuv\*\$J]', '', abc)

    # Convert the triplets to 'T' before braces are removed, so structure is preserved
    # abc = re.sub('\(3', 'T', abc)
    # abc = re.sub('[()]', '', abc)
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
    :return: Either '!!BAD ABC!!' or a valid abc string
    """

    # If the sone has first or second endings, we need to remove those first
    if '|1' in abc or ':|2' in abc:
        cleaned = remove_dual_repeat(abc, tune_id)
    # Otherwise, if it has repeats, we deal with those
    elif '|:' in abc or ':|' in abc:
        cleaned = remove_simple_repeats(abc, tune_id)
    # If there are no repeats, return the spaceless string
    else:
        cleaned = abc

    # abc = re.sub('(\|+]+)|(\[+\|+)|(\|+)', '|', abc)
    cleaned = cleaned.replace('!', '')
    while ']' in cleaned: cleaned = cleaned.replace(']', '|')

    # re.sub("[zabcdefgABCDEFG2345678()\]-^=_,></']", '', y)
    bars = cleaned.split('|')
    for y in bars:
        bar = y
        chars = [x for x in "zabcdefgABCDEFG23468()]-^=_,></'"]
        for z in chars:
            bar = bar.replace(z, '')
        if bar != '':
            # print(tune_id)
            cleaned = '!!BAD ABC - INVALID CHARS!!'
            break

    if '!!BAD ABC' in cleaned:
        # print_bad_abc(abc, tune_id)
        return '!!BAD ABC!!'

    while '||' in cleaned: cleaned = cleaned.replace('||', '|')
    if cleaned[0] == '|': cleaned = cleaned[1:]

    return cleaned


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
    return cleaned
# endregion
