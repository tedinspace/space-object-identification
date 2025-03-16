
from datetime import datetime

def timestamp_file():
    '''creates a timestamp string (ISO)'''
    return datetime.now().isoformat().replace('-','_').replace(':','_').split('.')[0]