# TEST

def remove_whitespace(abc):
    cleaned = ''.join(abc.split())

    if cleaned[:2] == 'C:':
        cleaned = cleaned[cleaned.index('|'):]
    if cleaned[:3] == '[|:' or cleaned[:3] == '||:':
        cleaned = '|:' + cleaned[3:]
    if cleaned[:2] == '[|':
        cleaned = cleaned[2:]
    if cleaned[:1] == '|' and cleaned[:2] != '|:':
        cleaned = cleaned[1:]
    if cleaned[0] == ':':
        cleaned = '|' + cleaned
    if cleaned[-1] == ':':
        cleaned = cleaned + '|'

    cleaned = cleaned.replace("\\", "")
    cleaned = cleaned.replace("\x14", "")
    cleaned = cleaned.replace('|]', '||')
    cleaned = cleaned.replace('::', ':||:')
    cleaned = cleaned.replace(':|:', ':||:')
    cleaned = cleaned.replace(':|||:', ':||:')
    return cleaned


def safe_abc(abc):
    # TODO - Make more robust, and elegant
    safe = True

    bad_chars = ['\"', 'V', 'T', 'K:', 'M', '{', '}', '~']
    for c in bad_chars:
        if c in abc:
            return False
    return safe


def remove_single_dual_repeat(abc, tune_id):
    temp = abc.split(':|2')
    end = temp.pop()
    if len(temp) == 0: return '!!BAD ABC - BLANK END2!!'
    x = temp[0]
    if x[:2] == '|:': x = x[2:]
    lrpt = x.count('|:')
    rrpt = x.count(':|')
    cleaned = ''

    try:
        if lrpt == 0 and rrpt == 0:
            beg, end1 = x.split('|1')
            cleaned = beg + '|' + end1 + '|' + beg + '|' + end + '|'
            cleaned = remove_repeats(cleaned, tune_id)

        elif lrpt == 1 and rrpt == 0:
            up, rem = x.split('|:')
            beg, end1 = rem.split('|1')
            cleaned = up + '|' + beg + '|' + end1 + '|' + beg + '|' + end + '|'
            cleaned = remove_repeats(cleaned, tune_id)

        else:
            subs = x.split(':|')
            if '|1' not in subs[-1]:
                raise ValueError

            elif len(subs) > 1:
                e = subs.pop()
                while '||' in e: e = e.replace('||', '|')
                if e[0] == ':': e = '|' + e
                for y in subs: cleaned += remove_simple_repeat(y + ':|', tune_id)
                end = remove_repeats(e + ':|2' + end, tune_id)
                cleaned += end
            else:
                x = subs[0]
                subs = x.split('|:')
                end = subs.pop() + ':|2' + end
                beg = '|:'.join(subs)

                beg = remove_simple_repeat(beg, tune_id)
                end = remove_repeats(end, tune_id)
                cleaned = beg + end

        if ':|' in cleaned or '|:' in cleaned:
            raise ValueError
        return cleaned
    except ValueError:
        return '!!BAD ABC - VALUE ERROR - SIMPLE!!'


def remove_dual_repeat(abc, tune_id):

    if len(abc) == 0:
        return ''
    elif abc[0] == '1' or abc[0] == ':':
        return '!!BAD ABC - MALFORM STRING!!'

    cleaned = ''
    abc = abc.replace(']|', '||')
    abc = abc.replace('|!|', '|||')
    syn1 = ['|[1', '[1', '1.']
    syn2 = [':|2.', ':|[2', ':||2', ':|||2', '|[2', ':|1']
    for x in syn1: abc = abc.replace(x, '|1')
    for x in syn2: abc = abc.replace(x, ':|2')
    count1 = abc.count('|1')
    count2 = abc.count(':|2')

    if count1 == count2:
        good_str = True
        temp = abc.split(':|2')
        end = temp.pop()
        for x in temp: good_str = good_str and ('|1' in x)

        if good_str:
            if len(temp) >= 2:
                try:
                    for x in range(count1):
                        loc1 = abc.index('|1') + 1
                        loc2 = abc.index(':|2') + 2
                        bars = 0
                        fin = loc2
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
                        fin -= 1
                        sub = abc[:fin]
                        abc = abc[fin:]
                        cleaned += remove_single_dual_repeat(sub, tune_id)
                except ValueError:
                    return '!!BAD ABC!!'

            elif len(temp) == 1:
                cleaned = remove_single_dual_repeat(abc, tune_id)
        else:
            return '!!BAD ABC - MISMATCH ENDS!!'

    elif count1 > count2:
        if abc.count('|2') != abc.count(':|2'):
            abc = abc.replace('|2', ':|2')
            abc = abc.replace('::|2', ':|2')
            cleaned = remove_dual_repeat(abc, tune_id)
        else:
            # TODO - 140? 100?
            #print(abc)
            return '!!BAD ABC - END1!!'
    elif count2 > count1:
        # TODO
        #print(abc)
        return '!!BAD ABC - END2!!'
    return cleaned


def remove_simple_repeat(abc, tune_id):
    cleaned = ''

    if abc.count(':|') > abc.count('|:'):
        temp = abc.split(':|')
        end = temp.pop()
        if '|:' in end:
            end = remove_simple_repeat(end, tune_id)
        for x in temp:
            if '|:' in x:
                cleaned += remove_simple_repeat(x, tune_id) + '|'
            else:
                cleaned += x + '|' + x + '|'
        cleaned += end + '|'

    elif abc.count(':|') <= abc.count('|:'):
        temp = abc.split('|:')
        beg = temp.pop(0)
        if ':|' in beg:
            cleaned = remove_simple_repeat(beg, tune_id)
        else:
            cleaned = beg + '|'
        for x in temp:
            if ':|' in x:
                cleaned += remove_simple_repeat(x, tune_id)
            else:
                cleaned += x + '|' + x + '|'
    return cleaned


def print_bad_abc(abc, tune_id, extra=list()):
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
    if '|1' in abc or ':|2' in abc or '|[1' in abc or ':|[2' in abc:
        cleaned = remove_dual_repeat(abc, tune_id)
    elif '|:' in abc or ':|' in abc:
        cleaned = remove_simple_repeat(abc, tune_id)
    else:
        cleaned = abc

    while '||' in cleaned: cleaned = cleaned.replace('||', '|')
    while '|]' in cleaned: cleaned = cleaned.replace('|]', '|')
    while '[|' in cleaned: cleaned = cleaned.replace('[|', '|')
    if cleaned[0] == '|': cleaned = cleaned[1:]

    if '!!BAD ABC' in cleaned:
        print_bad_abc(abc, tune_id)
        return '!!BAD ABC!!'

    return cleaned + "]"


def clean(abc, tune_id):
    cleaned = remove_whitespace(abc)
    cleaned = remove_repeats(cleaned, tune_id)
    return cleaned


