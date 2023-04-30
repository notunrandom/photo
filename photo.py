from datetime import datetime

def prepend_datetime(name, dt, dsep='.', tsep='.', sep='-'):
    return (
        f'{dt.year}{dsep}{dt.month:02}{dsep}{dt.day:02}{sep}'
        f'{dt.hour:02}{tsep}{dt.minute:02}{tsep}{dt.second:02}{sep}'
        f'{name}'
    )
