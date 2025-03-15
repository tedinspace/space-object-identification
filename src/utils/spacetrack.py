import configparser
from datetime import datetime
import requests

'''
these are helper functions that help us interact with the somewhat complicated space-track.org API

While this code is our own, it was based on the Python example on their site:
https://www.space-track.org/documentation#howto 

'''

URL_BASE = "https://www.space-track.org"
URL_LOGIN= "/ajaxauth/login"

# access satellite catalogs
URL_SATCAT_CURRENT = "/basicspacedata/query/class/satcat/format/json/orderby/NORAD_CAT_ID/CURRENT/Y/DECAY/null-val/"
URL_SATCAT_DECAYED = "/basicspacedata/query/class/satcat/format/json/orderby/NORAD_CAT_ID/CURRENT/Y/DECAY/<now"
URL_SATCAT_COMPLETE= "/basicspacedata/query/class/satcat/format/json/orderby/NORAD_CAT_ID/"

def loadSiteCred(FILE_WITH_PATH):
    '''load username in password from *.ini file to login to space-track'''
    config = configparser.ConfigParser()
    config.read(FILE_WITH_PATH)
    configUsr = config.get("configuration","username")
    configPwd = config.get("configuration","password")
    return {'identity': configUsr, 'password': configPwd} # NEVER PRINT THIS

def api_login(session, credentials):
    '''log into space-track.org in order to access api'''
    resp =  session.post(URL_BASE + URL_LOGIN, data = credentials)
    if resp.status_code != 200:
        raise Exception("unable to log into space-track; check that .ini file exists")
    return resp

def api_current_satellite_catalog(session):
    resp =  session.get(URL_BASE + URL_SATCAT_CURRENT)
    if resp.status_code != 200:
        raise Exception("unable to access api")
    return resp

def api_decayed_satellite_catalog(session):
    resp =  session.get(URL_BASE + URL_SATCAT_DECAYED)
    if resp.status_code != 200:
        raise Exception("unable to access api")
    return resp

def timestamp():
    '''creates a timestamp string (ISO)'''
    return datetime.now().isoformat().replace('-','_').replace(':','_').split('.')[0]

def request_repull_current_and_decayed_satcats(credentials_path, ):
    '''start to finish request for repulling satcats; 
    
    this isn't a call you should make often (or ever)'''
    CREDENTIALS_NEVER_PRINT = loadSiteCred(credentials_path)

    with requests.Session() as session:
        api_login(session, CREDENTIALS_NEVER_PRINT)
        satcat_curr_resp = api_current_satellite_catalog(session)
        satcat_decay_resp = api_decayed_satellite_catalog(session)

    session.close()
    return [satcat_curr_resp.text, satcat_decay_resp.text ]
