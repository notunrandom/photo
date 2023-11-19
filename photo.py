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


def normalise_dir_ops(path):
    # TODO Do I still need this?

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
    # TODO Do I still need this?
    path = pathlib.Path(pathstring)
    apply_ops(normalise_dir_ops(path))


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


def organise_ops(orig, dest):
    dirs = set()
    move = set()
    for f in orig.rglob('*'):
        if f.is_file():
            try:
                datetime = datetime_original(f)
                subdir = path_from_datetime(datetime)
                name = time_stamp_file_name(f.name, datetime)
            except KeyError:
                try:
                    datetime = datetime_from_name(f.name)
                    subdir = path_from_datetime(datetime)
                    name = time_stamp_file_name(f.name, datetime)
                except Exception:
                    subdir = 'sinediem'
                    name = f.name
            dirs.add(subdir)
            move.add((f, dest/subdir/name))
    ops = [(ensure_dir, dest/d) for d in dirs]
    ops += [(rename, x, y) for x, y in move]
    return ops


def analysis(path):
    files = Counter()
    unique = Counter()
    sinediem = []

    for f in pathlib.Path(path).rglob('*'):
        if f.is_file():
            files[f.suffix] += 1
            try:
                dt = datetime_original(f.as_posix())
                unique[(dt, f.name)] += 1
            except KeyError:
                try:
                    dt = datetime_from_name(f.name)
                    unique[(dt, f.name)] += 1
                except Exception:
                    sinediem.append((f.name, f.as_posix()))

    names = Counter([x for x, y in sinediem])
    clashes = len(unique - Counter(list(unique)))
    clashes += len(names - Counter(list(names)))
    return files, sinediem, clashes


def list_dir(path):
    result = set()
    for f in pathlib.Path(path).rglob('*'):
        if f.is_file():
            try:
                datetime = datetime_original(f)
            except KeyError:
                datetime = None

            result.add((f.resolve().parts, datetime))
    return result
