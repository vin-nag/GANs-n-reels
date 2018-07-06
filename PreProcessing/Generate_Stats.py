from datetime import datetime

# TODO - Sort the data prior to printing
total = 0
unique = set()
family = dict()
meter = dict()
mode = dict()
mode_types = dict()
mode_count = dict()


def read_list(tunes):
    global total

    def inc(key, master):
        if key in master:
            master[key] += 1
        else:
            master[key] = 0

    for t in tunes:
        unique.add(int(t['tune']))
        inc(t['type'], family)
        inc(t['meter'], meter)
        inc(t['mode'], mode)
        total += 1

    for x in mode:
        s = str(x)
        X = s[0]
        s = s[1:]
        if s in mode_types:
            mode_types[s].append(X)
            mode_count[s] += mode[x]
        else:
            mode_types[s] = [X]
            mode_count[s] = mode[x]


def print_dict(d, s=None):
    out = ""
    if s:
        out += str(len(d)) + " different types of " + s + " were found.\n"
    for x in d:
        s = '{message: <14}'.format(message=x)
        c = '{message: <5}'.format(message=str(d[x]))
        p = '{:8.2f}'.format(100*d[x]/total) + "%"
        out += s + " - " + c + " / " + str(total) + " --> " + p + "\n"
    out += "\n\n"
    return out


def print_dict2(d, s=None):
    out = ""
    if s:
        out += str(len(d)) + " different types of " + s + " were found.\n"
    for x in d:
        s = '{message: <14}'.format(message=x)
        print()
        out += s + " - " + str(d[x]) + "\n"
    out += "\n\n"
    return out


def parse_stats(tunes, outfile=None):
    read_list(tunes)

    out = "\n" + str(datetime.now()) + "\n\n"
    out += 'A total of ' + str(total) + ' tunes were scanned.\n'
    out += 'Max unique tune id is: ' + str(max(unique)) + "\n\n"
    out += print_dict(family, "SONG STYLES")
    out += print_dict(meter, "TIME SIGNATURES")
    out += print_dict(mode, "KEY SIGNATURES")
    out += print_dict2(mode_types, "MODE TYPES")
    out += print_dict(mode_count)

    if outfile:
        with open(outfile, 'w') as f:
            f.write(out)
    else:
        print(out)


if __name__ == '__main__':
    from Tunes import Tunes_raw
    tunes = Tunes_raw.tunes
    parse_stats(tunes, '../Tunes/Stats_raw.txt')
