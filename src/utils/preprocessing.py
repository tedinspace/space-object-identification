import zipfile
import json
import utils.TLE as TLE

def loadSeveralYearsOfUnprocessedStates(file_name_array):
     '''take several file paths for TLE snapshots and unloads them into one big array'''
     snapshot_states=[]
     for name in file_name_array:
          snapshot_states = [*snapshot_states, * loadUnprocessedStateSnapshots(name)]
     return snapshot_states

def loadUnprocessedStateSnapshots(file_name_with_path):
    '''returns list unprocessed TLEs'''
    snapshot_states = []
    with zipfile.ZipFile(file_name_with_path) as z:
            file_list = z.namelist()
            text_files = [file for file in file_list if file.startswith("snapshots/snapshot_states_") and file.endswith('.txt')]
            for file_name in text_files:
                with z.open(file_name) as f:
                    decoded_content = f.read().decode('utf-8').split("\r\n")

                    snapshot_states = [*snapshot_states, *removeDuplicateRSOsInSnapshot(decoded_content)]
    return snapshot_states

def removeDuplicateRSOsInSnapshot(states):
     '''intended to remove duplicate objects in a single day/snapshot'''
     saved_states =[]
     found_rsos = set()
     for idx in range(0,len(states),3):
          if states[idx].startswith("0 "):
               L0 = states[idx]
               L1 = states[idx+1]
               L2 = states[idx+2]
               rso_number = TLE.rso_no_zero(L1)
               if rso_number not in found_rsos:
                    saved_states.append(L0)
                    saved_states.append(L1)
                    saved_states.append(L2)
               
               found_rsos.add(rso_number)
     return saved_states

def loadUnprocessedSatCat_current(file_name_with_path):
     '''load the unprocessed satcat json'''
     with zipfile.ZipFile(file_name_with_path) as z:
          with z.open("satcat/current_satcat_2025_03_16T20_46_53.json") as f:
               data = json.load(f)
     return data


def loadUnprocessedSatCat_decayed(file_name_with_path):
     '''load the unprocessed satcat (decayed) json'''
     with zipfile.ZipFile(file_name_with_path) as z:
          with z.open("satcat/decayed_satcat_2025_03_16T20_46_53.json") as f:
               data = json.load(f)
     return data


def deduplicateAndMergeDataSources(snapshot_states, satCat_current, satCat_decayed):
     '''master logic for merging snapshots and satellite catalogs; also performs deduplication and SMA/ap/per/regime calculations'''
     deduplication_record = {}
     uncataloged_states = {}
     nDuplicatesFound = 0

     aggregatedData = {
          'NUMBER': [],
          'NAME': [],
          'TYPE': [],
          'RCS': [],
          'IS_CURRENT': [],
          'REGIME': [],
          'EPOCH': [],
          # VIA LINE 2
          'INCL': [],
          'RAAN': [],
          'ECC': [],
          'ARG_PER': [],
          'MEAN_ANOM': [],
          'MEAN_MOTION': [], 
          'SMA_KM': [],
          'APOGEE_KM': [],
          'PERIGEE_KM': [],
          # VIA LINE 1
          'MEAN_MOTION_1ST_DER': [],
          # other
          'COUNTRY':[],
          # save tle
          'LINE1': [],
          'LINE2': [],

     }
     for idx in range(0,len(snapshot_states),3):
          if snapshot_states[idx].startswith("0 "):
               # unpack 3LE
               L0 = snapshot_states[idx]
               L1 = snapshot_states[idx+1]
               L2 = snapshot_states[idx+2]
               rso_number = TLE.rso_no_zero(L1)
               
               # 1. Check for duplicate states
               if rso_number not in deduplication_record:
                    deduplication_record[rso_number]= set()
                    
               if L1 not in deduplication_record[rso_number]:
                    deduplication_record[rso_number].add(L1)
               else:
                    nDuplicatesFound+=1
                    #print("found duplicate state for "+rso_number+"; skipping...")
                    continue

               # 2. try to pull satcat information for RSO
               not_decayed = 1
               if rso_number in satCat_current.index:
                    satcat_entry = satCat_current.loc[rso_number] # active state
               elif rso_number in satCat_decayed.index:
                    satcat_entry = satCat_decayed.loc[rso_number] # decayed state
                    not_decayed = 0
               else:
                    if rso_number not in uncataloged_states:
                         uncataloged_states[rso_number]=[]
                    uncataloged_states[rso_number].append([L0, L1, L2])
                    satcat_entry = {}
               
               # 3. if there's a satcat entry 
               if len(satcat_entry)>0:

                    ecc = TLE.tle_ecc(L2)
                    mm = TLE.tle_meanmotion(L2)
                    sma = TLE.compute_SMA(mm)
                    apogee = TLE.compute_apogee(sma,ecc)
                    perigee = TLE.compute_perigee(sma, ecc)
               
                    aggregatedData["NUMBER"].append(rso_number)
                    aggregatedData["NAME"].append(satcat_entry["SATNAME"].strip())
                    aggregatedData["TYPE"].append(satcat_entry["OBJECT_TYPE"].strip())
                    aggregatedData["RCS"].append(satcat_entry["RCS_SIZE"] if satcat_entry["RCS_SIZE"] is not None else "NA")
                    aggregatedData["IS_CURRENT"].append(not_decayed)

                    aggregatedData["REGIME"].append(TLE.compute_regime(apogee, perigee))
                    aggregatedData["EPOCH"].append(TLE.tle_epoch(L1))
                    
                    aggregatedData["INCL"].append(TLE.tle_incl(L2))
                    aggregatedData["RAAN"].append(TLE.tle_RAAN(L2))
                   
                    aggregatedData["ECC"].append(ecc)
                    aggregatedData["ARG_PER"].append(TLE.tle_argper(L2))
                    aggregatedData["MEAN_ANOM"].append(TLE.tle_meananom(L2))
                    
                    aggregatedData["MEAN_MOTION"].append(mm)
                    aggregatedData["SMA_KM"].append(sma)
                    aggregatedData["APOGEE_KM"].append(apogee)
                    aggregatedData["PERIGEE_KM"].append(perigee)

                    aggregatedData["MEAN_MOTION_1ST_DER"].append(TLE.tle_meanmotion_1st_der(L1))

                    aggregatedData["COUNTRY"].append(satcat_entry["COUNTRY"].strip())

                    aggregatedData["LINE1"].append(L1)
                    aggregatedData["LINE2"].append(L2)



     return aggregatedData, uncataloged_states, nDuplicatesFound