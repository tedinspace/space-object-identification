
import math
mu = 3.9860044188e14 # [m^3 s^-2]
earthrad = 6378.1 # [km]

def rso(L1):
    '''return rso number; allows leading zeros'''
    return  L1[2:7].strip()
def rso_no_zero(L1):
    '''returns rso number withtout leading zeros'''
    return rso(L1).lstrip('0')
def name(L0):
    '''unpacks name from L0 of 3LE'''
    return L0.split("0 ")[1].strip()

def tle_epoch(L1):
    '''unpacks epoch from line 1'''
    return float(L1[18:32].strip())

def tle_meanmotion_1st_der(L1):
    '''unpacks first deriv of MM from line 1'''
    return float(L1[33:43].strip())


def handle_no_decimal(tmp_str):
    '''helper function that handles values with implied zero and truncated exponents'''
    is_neg = False
    if tmp_str[0]=='-':
        tmp_str = tmp_str[1:]
        is_neg = True
    tmp_arr = tmp_str.split('-')
    
    if len(tmp_arr)==2:
        tmp_str = tmp_arr[0]+'e-'+tmp_arr[1]
        
    else:
        tmp_arr = tmp_str.split('+')
        tmp_str = tmp_arr[0]+'e+'+tmp_arr[1]
    
    if is_neg:
        tmp_str = "-0."+tmp_str
    else:
        tmp_str = "0."+tmp_str
    return float(tmp_str)
def tle_meanmotion_2nd_der(L1):
    '''unpacks send deriv of MM from line 1'''
    return handle_no_decimal(L1[44:52].strip())

def tle_b_star(L1):
    '''b-star/ Draf coefficient'''
    return handle_no_decimal(L1[54:61].strip())

def tle_incl(L2):
    '''unpacks inclination from line 2'''
    return float(L2[8:16].strip())

def tle_RAAN(L2):
    '''unpacks RAAN from line 2'''
    return float(L2[17:25].strip())

def tle_ecc(L2):
    '''unpacks eccentricity from L2'''
    return float("0."+L2[26:33].strip())

def tle_argper(L2):
    '''unpacks argper from line 2'''
    return float(L2[34:42].strip())

def tle_meananom(L2):
    '''unpacks mean ano from line2'''
    return float(L2[43:51].strip())

def tle_meanmotion(L2):
    '''unpacks mean motion from line 2'''
    return float(L2[52:63].strip())

def compute_SMA(mean_motion):
    '''computes semi-major axis'''
    return ((mu)**(1/3)/((2*math.pi*mean_motion)/(86400))**(2/3))/1000

def compute_apogee(sma, ecc):
    '''computes apogee'''
    return sma*(1+ecc) - earthrad

def compute_perigee(sma, ecc):
    '''computes perigee'''
    return sma*(1-ecc) - earthrad

def compute_regime(a, p):
    ''' computes orbital regime; @source Vallado '''
    a = a + earthrad
    p = p + earthrad

    REG_1a = (p<1.13*earthrad  and p>earthrad      and a<2*earthrad)
    REG_1b = (p>=1.13*earthrad and p<1.75*earthrad and a<2*earthrad)
    REG_2  = (p<1.75*earthrad  and a>=2*earthrad   and a<7.5*earthrad)
    REG_3  = (p>=1.75*earthrad and p<3.75*earthrad and a<6*earthrad)
    REG_4  = (p>=3.75*earthrad and p<5.2*earthrad  and a>=2.75*earthrad and a<6*earthrad)
    REG_5  = (p>=5.2*earthrad  and p<7.5*earthrad  and a>=5.2*earthrad  and a<7.5*earthrad)
    REG_6  = (p>=1.75*earthrad and p<5.2*earthrad  and a>=6*earthrad    and a<7.5*earthrad)
    REG_7  = (p>=1.75*earthrad and a>=7.5*earthrad)
    REG_8  = (p<1.75*earthrad  and a<=7.5*earthrad)
    REG_9 = ( a>earthrad*6 and p< earthrad*1.9)
    
    if REG_1a or REG_1b:
        return "LEO" 
    if REG_4:
        return "MEO"
    if REG_5:
        return "GEO"
    if REG_2 or REG_3 or REG_6 or REG_7 or REG_8 or REG_9:
        return "HEO"
    return "OTHER"