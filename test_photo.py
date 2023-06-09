from datetime import datetime
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


def test_iso8601_ext():
    dt1 = datetime(1, 1, 1, 0, 0)
    assert photo.iso8601_ext(dt1) == "0001-01-01"
    dt2 = datetime(1987, 3, 5, 0, 12, 59)
    assert photo.iso8601_ext(dt2) == "1987-03-05"
    assert photo.iso8601_ext(dt2, precision='month') == "1987-03"
    assert photo.iso8601_ext(dt2, precision='year') == "1987"


def test_time_stamp_file_name():
    name = "NDX_1234.RAW"
    dt = datetime(2010, 4, 15, 16, 22, 9)
    new_name = photo.time_stamp_file_name(name, dt)
    assert new_name == "20100415T162209-NDX_1234.RAW"
    new_name = photo.time_stamp_file_name(name, dt, sep='___')
    assert new_name == "20100415T162209___NDX_1234.RAW"
    with pytest.raises(photo.IllegalSeparator):
        new_name = photo.time_stamp_file_name(name, dt, sep=':')


def test_path_from_datetime():
    dt = datetime(1995, 3, 17, 9, 5, 59)
    path = photo.path_from_datetime(dt)
    assert path == "1995/1995-03"


def test_normalise_name_case():
    assert photo.normalise_name('2003-CSEE-001.jpg') == '2003-csee-001.jpg'


def test_datetime_original():
    result = photo.datetime_original('test.jpg')
    assert result == datetime(2023, 5, 28, 11, 53, 20)


def test_normalise_dir_ops(tmp_path):
    assert [p.name for p in tmp_path.iterdir()] == []
    files = ['2005-lowercase.jpg', '2004-UPPER.jpg', '1999-CamelCase.png']
    paths = [tmp_path / f for f in files]
    for p in paths:
        p.touch()
    opers = photo.normalise_dir_ops(tmp_path)
    names = [(op, p.name, q.name) for (op, p, q) in opers]
    assert names == [
            (photo.rename, '1999-CamelCase.png', '1999-camelcase.png'),
            (photo.rename, '2004-UPPER.jpg', '2004-upper.jpg')
            ]


def test_apply_ops(tmp_path):
    CONTENT = 'Unimportant'
    NAME1 = 'blabla.txt'
    NAME2 = 'yohoho.xyz'
    assert [p for p in tmp_path.iterdir()] == []
    file1 = tmp_path/NAME1
    file1.write_text(CONTENT)
    assert [p for p in tmp_path.iterdir()] == [file1]
    file2 = tmp_path/NAME2
    ops = [(photo.rename, file1, file2)]
    photo.apply_ops(ops)
    assert [p.name for p in tmp_path.iterdir()] == [NAME2]
    assert file2.read_text() == CONTENT
