import pathlib
from datetime import datetime

from PIL import Image
from PIL import ExifTags


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


def normalise_dir_ops(path):
    names = [p.name for p in path.iterdir() if p.is_file()]
    normal = [normalise_name(name) for name in names]
    changed = [(was, now) for was, now in zip(names, normal) if now != was]
    return [(rename, path/was, path/now) for was, now in changed]


def apply_ops(ops):
    for op, *args in ops:
        op(*args)


def rename(old, new):
    old.rename(new)


def normalise_dir(pathstring='.'):
    path = pathlib.Path(pathstring)
    apply_ops(normalise_dir_ops(path))


def datetime_original(filename):
    with Image.open(filename) as img:
        tags = img.getexif().get_ifd(ExifTags.IFD.Exif)
        dtstring = tags[ExifTags.Base.DateTimeOriginal]
        return datetime.strptime(dtstring, '%Y:%m:%d %H:%M:%S')


def ensure_dir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def organise_ops(orig, dest):
    dirs = set()
    move = set()
    for f in orig.rglob('*'):
        if f.is_file():
            datetime = datetime_original(f)
            subdir = path_from_datetime(datetime)
            dirs.add(subdir)
            name = time_stamp_file_name(f.name, datetime)
            move.add((f, dest/subdir/name))
    ops = [(ensure_dir, dest/d) for d in dirs]
    ops += [(rename, x, y) for x, y in move]
    return ops
