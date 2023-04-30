from datetime import datetime

def iso8601(dt):
    '''Convert a datetime to basic ISO 8601 format, e.g. 19840329T123300.

    At this time datetime.isoformat() can only generate the extended ISO 8601 format.
    The extended format contains colons. Colons are not valid in filenames on Mac OS.
    This function produces a standard ISO 8601 datetime string which is usable in
    file and directory names.
    '''
    return f'{dt.year:04}{dt.month:02}{dt.day:02}T{dt.hour:02}{dt.minute:02}{dt.second:02}'

def iso8601_ext(dt, precision='day'):
    '''Convert a datetime to extended ISO 8601 format, e.g. 1984-03-29.

    At this time datetime.isoformat() does not provide the option of specifying precision.
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
    if not set(sep) <= set('-_.'): raise IllegalSeparator
    return iso8601(dt) + sep + name

def path_from_datetime(dt):
    return '/'.join([iso8601_ext(dt, precision=p) for p in ['year', 'month']])

