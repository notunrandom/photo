from datetime import datetime
from pathlib import Path
import pytest

import photo


def test_iso8601():
    table = (
            ((1987, 3, 5, 0, 12, 59), "19870305T001259"),
            ((1, 1, 1, 0, 0), "00010101T000000"),
            ((9999, 12, 31, 23, 59, 59), "99991231T235959"),
            ((1987, 3, 5, 0, 12, 59, 359), "19870305T001259")
            )
    for inp, out in table:
        assert photo.iso8601(datetime(*inp)) == out


def test_time_stamp_file_name():
    name = "NDX_1234.RAW"
    dt = datetime(2010, 4, 15, 16, 22, 9)
    new_name = photo.time_stamp_file_name(name, dt)
    assert new_name == "20100415T162209-NDX_1234.RAW"
    new_name = photo.time_stamp_file_name(name, dt, sep='___')
    assert new_name == "20100415T162209___NDX_1234.RAW"
    with pytest.raises(photo.IllegalSeparator):
        new_name = photo.time_stamp_file_name(name, dt, sep=':')


def test_time_stamp_no_duplication():
    name = "2010-04-12--12-23_NDX_1234.RAW"
    dt = datetime(2010, 4, 15, 16, 22, 9)
    new_name = photo.time_stamp_file_name(name, dt)
    assert new_name == "20100415T162209-NDX_1234.RAW"


def test_path_from_datetime():
    dt = datetime(1995, 3, 17, 9, 5, 59)
    path = photo.path_from_datetime(dt)
    assert path == Path("1995/03")


def test_normalise_name_case():
    assert photo.normalise_name('2003-CSEE-001.jpg') == '2003-csee-001.jpg'


def test_datetime_original():
    result = photo.datetime_original('tests/photos/photo1.jpg')
    assert result == datetime(2023, 5, 28, 11, 53, 20)


def test_datetime_from_name():
    dt = photo.datetime_from_name('20190728-142356-photo5.jpg')
    assert dt == datetime(2019, 7, 28, 14, 23, 56)
    dt = photo.datetime_from_name('1970-08-23--12:23:56_NDX-1234.jpg')
    assert dt == datetime(1970, 8, 23, 12, 23, 56)


def test_apply_rename_op(tmp_path):
    assert [p for p in tmp_path.iterdir()] == []
    CONTENT = 'Unimportant'
    NAME1 = 'blabla.txt'
    NAME2 = 'yohoho.xyz'
    file1 = tmp_path/NAME1
    file1.write_text(CONTENT)
    assert [p for p in tmp_path.iterdir()] == [file1]
    file2 = tmp_path/NAME2
    photo.apply_ops([(photo.rename, file1, file2)])
    assert [p.name for p in tmp_path.iterdir()] == [NAME2]
    assert file2.read_text() == CONTENT


def test_apply_ensure_dir_op(tmp_path):
    assert [p.name for p in tmp_path.iterdir()] == []
    NAME1 = 'newdir'
    NAME2 = 'subdir'

    # Will create parent (intermediate) dirs if necessary
    newdir = tmp_path/NAME1/NAME2
    photo.apply_ops([(photo.ensure_dir, newdir)])
    assert [p.name for p in tmp_path.iterdir()] == [NAME1]
    assert [p.name for p in (tmp_path/NAME1).iterdir()] == [NAME2]
    assert Path(newdir).is_dir() is True

    # OK if already exists !
    photo.apply_ops([(photo.ensure_dir, newdir)])
    assert [p.name for p in tmp_path.iterdir()] == [NAME1]
    assert [p.name for p in (tmp_path/NAME1).iterdir()] == [NAME2]
    assert Path(newdir).is_dir() is True


def test_organise_ops():
    DEST = Path('somewhere')
    ORIG = Path('/')
    origin = [
        ('/', 'photo1.jpg', datetime(2023, 5, 28, 11, 53, 20)),
        ('/', 'dir1', 'photo2.jpg', datetime(2023, 7, 18, 15, 24, 49)),
        ('/', 'dir1', 'dir2', 'photo3.jpg', datetime(2023, 7, 18, 15, 29, 23)),
        ('/', 'photo1.png', datetime(2023, 5, 28, 11, 53, 20)),
        ('/', 'photo4.png', None),
        ('/', '20190728-142356-photo5.jpg', datetime(2019, 7, 28, 14, 23, 56)),
        ]
    ops = photo.organise_ops(origin, DEST)

    # Creation of necessary dated directories
    paths = [DEST/'sinediem'] + [DEST/'2023'/p for p in ['05', '07']]
    for path in paths:
        assert (photo.ensure_dir, path) in ops

    # Rename photos and move to appropriate directory by date
    files = [(ORIG/'photo1.jpg',
              DEST/'2023'/'05'/'20230528T115320-photo1.jpg'),
             (ORIG/'dir1'/'photo2.jpg',
              DEST/'2023'/'07'/'20230718T152449-photo2.jpg'),
             (ORIG/'dir1'/'dir2'/'photo3.jpg',
              DEST/'2023'/'07'/'20230718T152923-photo3.jpg')]
    for orig, dest in files:
        assert (photo.rename, orig, dest) in ops

    # Files with same timestamp but different name/extension are OK
    files = [(ORIG/'photo1.png',
              DEST/'2023'/'05'/'20230528T115320-photo1.png')]
    for orig, dest in files:
        assert (photo.rename, orig, dest) in ops

    # Files with same timestamp but different name/extension are OK
    files = [(ORIG/'photo1.png',
              DEST/'2023'/'05'/'20230528T115320-photo1.png')]
    for orig, dest in files:
        assert (photo.rename, orig, dest) in ops

    # Files without DateTimeOriginal get put in specific directory...
    files = [(ORIG/'photo4.png',
              DEST/'sinediem'/'photo4.png')]
    for orig, dest in files:
        assert (photo.rename, orig, dest) in ops

    # ... unless there is date information in their name
    files = [(ORIG/'20190728-142356-photo5.jpg',
              DEST/'2019'/'07'/'20190728T142356-photo5.jpg')]
    for orig, dest in files:
        assert (photo.rename, orig, dest) in ops


def test_analysis():
    files = [
        ('/', 'photo1.jpg', datetime(2023, 5, 28, 11, 53, 20)),
        ('/', 'dir1', 'photo2.jpg', datetime(2023, 7, 18, 15, 24, 49)),
        ('/', 'dir1', 'dir2', 'photo3.jpg', datetime(2023, 7, 18, 15, 29, 23)),
        ('/', 'photo1.png', datetime(2023, 5, 28, 11, 53, 20)),
        ('/', 'photo4.png', None),
        ('/', '20190728-142356-photo5.jpg', datetime(2019, 7, 28, 14, 23, 56)),
        ]
    (suffixes, sinediem, clashes) = photo.analysis(files)
    assert suffixes.total() == 6
    assert suffixes['.jpg'] == 4
    assert len(sinediem) == 1
    assert clashes == 0


def test_list_dir():
    ORIG = Path('tests/photos').resolve()
    files = photo.list_dir(ORIG)
    orig = ORIG.parts
    table = [
            ('photo1.jpg', datetime(2023, 5, 28, 11, 53, 20)),
            ('dir1', 'photo2.jpg', datetime(2023, 7, 18, 15, 24, 49)),
            ('20190728-142356-photo5.jpg', None),
            ('photo4.png', None)
            ]
    for *parts, dt in table:
        full = orig + tuple(parts) + (dt,)
        assert full in files


def test_fill():
    files = [
        ('/', 'dir1', 'photo2.jpg', datetime(2023, 7, 18, 15, 24, 49)),
        ('/', 'photo4.png', None),
        ('/', '20190728-142356-photo5.jpg', None),
        ]
    root = Path('/').parts
    table = [
            ('dir1', 'photo2.jpg', datetime(2023, 7, 18, 15, 24, 49)),
            ('20190728-142356-photo5.jpg', None),
            ('photo4.png', None)
            ]
    for *parts, dt in table:
        full = root + tuple(parts) + (dt,)
        assert full in files

    filled = photo.fill_missing_datetimes(files)
    added = datetime(2019, 7, 28, 14, 23, 56)
    table[1] = ('20190728-142356-photo5.jpg', added)

    for *parts, dt in table:
        full = root + tuple(parts) + (dt,)
        assert full in filled
