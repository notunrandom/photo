import os
from datetime import datetime
import photo

def test_prepend_datetime():
    name = "NDX_1234.RAW" 
    dt = datetime(2010, 4, 15, 16, 22, 9)
    new_name = photo.prepend_datetime(name, dt)
    assert new_name == "2010.04.15-16.22.09-NDX_1234.RAW"
    new_name = photo.prepend_datetime(name, dt, dsep='-', tsep=':', sep='--')
    assert new_name == "2010-04-15--16:22:09--NDX_1234.RAW"
