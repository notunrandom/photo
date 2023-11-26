import pathlib
import string
from datetime import datetime
from collections import Counter

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


class IllegalSeparator(Exception):
    pass


def time_stamp_file_name(name, dt, sep='-'):
    if not set(sep) <= set('-_.'):
        raise IllegalSeparator
    return iso8601(dt) + sep + name.lstrip(string.digits + string.punctuation)


def path_from_datetime(dt):
    iso = iso8601(dt)
    year = iso[:4]
    month = iso[:6]
    return '/'.join([year, month])


def normalise_name(name):
    return name.lower()


def apply_ops(ops):
    for op, *args in ops:
        op(*args)


def rename(old, new):
    old.rename(new)


def datetime_original(filename):
    with Image.open(filename) as img:
        tags = img.getexif().get_ifd(ExifTags.IFD.Exif)
        dtstring = tags[ExifTags.Base.DateTimeOriginal]
        return datetime.strptime(dtstring, '%Y:%m:%d %H:%M:%S')


def datetime_from_name(filename):
    dtstring = ''.join(filter(str.isdigit, filename))[:14]
    return datetime.strptime(dtstring, '%Y%m%d%H%M%S')


def ensure_dir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def organise_ops(files, dest):

    dirs = set()
    move = set()

    for *parts, dt in files:
        *path, name = parts
        if dt is None:
            subdir = 'sinediem'
        else:
            subdir = path_from_datetime(dt)
            assert type(name) is str
            name = time_stamp_file_name(name, dt)

        dirs.add(subdir)
        move.add((pathlib.PurePath(*parts), dest/subdir/name))

    ops = [(ensure_dir, dest/d) for d in dirs]
    ops += [(rename, x, y) for x, y in move]
    return ops


def analysis(files):

    suffixes = Counter()
    unique = Counter()
    sinediem = []

    for *parts, dt in files:
        *path, name = parts
        suffix = pathlib.PurePath(name).suffix
        suffixes[suffix] += 1
        if dt is None:
            sinediem.append(parts)
        else:
            unique[(dt, name)] += 1

    names = Counter([n for *p, n in sinediem])
    clashes = len(unique - Counter(list(unique)))
    clashes += len(names - Counter(list(names)))
    return suffixes, sinediem, clashes


def list_dir(path):
    result = set()
    for f in pathlib.Path(path).rglob('*'):
        if f.is_file():
            try:
                datetime = datetime_original(f)
            except KeyError:
                datetime = None
            result.add(f.resolve().parts + (datetime,))
    return result


def fill_missing_datetimes(files):
    def fill(file):
        *dirs, name, dt = file
        if dt is None:
            try:
                dt = datetime_from_name(name)
            except Exception:
                pass
        return (*dirs, name, dt)

    return set(map(fill, files))
