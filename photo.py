from enum import Enum


FileOp = Enum('FileOp', ['RENAME'])


def iso8601(dt):
    '''Convert a datetime to basic ISO 8601 format.

    Example: 19840329T123300.

    At this time datetime.isoformat() can only generate the extended
    ISO 8601 format. The extended format contains colons. Colons are
    not valid in filenames on Mac OS. This function produces a standard
    ISO 8601 datetime string which is usable in file and directory
    names.
    '''
    year, mth, day, hour, min_, sec = (dt.year, dt.month, dt.day,
                                       dt.hour, dt.minute, dt.second)
    return f'{year:04}{mth:02}{day:02}T{hour:02}{min_:02}{sec:02}'


def iso8601_ext(dt, precision='day'):
    '''Convert a datetime to extended ISO 8601 format, e.g. 1984-03-29.

    At this time datetime.isoformat() does not provide the option of
    specifying precision.
    '''
    result = f'{dt.year:04}'
    if precision != 'year':
        result += f'-{dt.month:02}'
        if precision != 'month':
            result += f'-{dt.day:02}'
    return result


class IllegalSeparator(Exception):
    pass


def time_stamp_file_name(name, dt, sep='-'):
    if not set(sep) <= set('-_.'):
        raise IllegalSeparator
    return iso8601(dt) + sep + name


def path_from_datetime(dt):
    return '/'.join([iso8601_ext(dt, precision=p) for p in ['year', 'month']])


def normalise_name(name):
    return name.lower()


def normalise_dir_ops(files):
    normal = [normalise_name(file) for file in files]
    changed = [(was, now) for was, now in zip(files, normal) if now != was]
    return [(FileOp.RENAME, was, now) for was, now in changed]
