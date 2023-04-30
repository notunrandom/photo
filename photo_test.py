from datetime import datetime
import photo
import pytest

def test_iso8601():
    assert photo.iso8601(datetime(1987,  3,  5,  0, 12, 59)) == "19870305T001259"
    assert photo.iso8601(datetime(   1,  1,  1,  0,  0    )) == "00010101T000000"
    assert photo.iso8601(datetime(9999, 12, 31, 23, 59, 59)) == "99991231T235959"
    assert photo.iso8601(datetime(1987,  3,  5,  0, 12, 59, 359)) == "19870305T001259"

def test_iso8601_ext():
    assert photo.iso8601_ext(datetime(1987,  3,  5,  0, 12, 59)) == "1987-03-05"
    assert photo.iso8601_ext(datetime(   1,  1,  1,  0,  0    )) == "0001-01-01"
    assert photo.iso8601_ext(datetime(1987,  3,  5,  0, 12, 59), precision='month') == "1987-03"
    assert photo.iso8601_ext(datetime(1987,  3,  5,  0, 12, 59), precision='year')  == "1987"

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
