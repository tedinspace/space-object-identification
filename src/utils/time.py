
from datetime import datetime, timedelta

def timestamp_file_now():
    '''iso now file timestamp'''
    return timestampe_file(datetime.now())

def timestampe_file(datetime_obj):
    '''make a timestamp string that can be put into a file name'''
    return datetime_obj.isoformat().replace('-','_').replace(':','_').split('.')[0]

def timestamp_query(datetime_object):
    '''YYYY-MM-DD iso string'''
    return datetime_object.strftime('%Y-%m-%d')


def year_doy_to_datetime(epoch):
    year = int(epoch // 1000)
    day_of_year = epoch % 1000
    year += 2000 if year < 57 else 1900
    return  datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
