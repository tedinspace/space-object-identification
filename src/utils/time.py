
from datetime import datetime

def timestamp_file_now():
    '''iso now file timestamp'''
    return timestampe_file(datetime.now())

def timestampe_file(datetime_obj):
    '''make a timestamp string that can be put into a file name'''
    return datetime_obj.isoformat().replace('-','_').replace(':','_').split('.')[0]

def timestamp_query(datetime_object):
    '''YYYY-MM-DD iso string'''
    return datetime_object.strftime('%Y-%m-%d')