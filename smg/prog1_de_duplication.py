# -*- coding: utf-8 -*-
"""
BASIC Key Replacement
    - Takes entire collection and creates a new collection with replaced keys
    - also deduplicates raw keys sent multiple times and keeps most recent in new collection
    - connection logic based on Saminus aggregate by date
    - so depends on existence of .env file for connectivity
    - and for PROD, must be executed from AWS VPC to connect

@author: dan
"""

# =============================================================================
# STEP 0: Basic setup and connect
# =============================================================================


import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())

# use DEV_MONGO_DATABASE_URI for dev and PROD_MONGO_DATABASE_URI for documentDB
CONNECTION_STRING = os.getenv('PROD_MONGO_DATABASE_URI')
#CONNECTION_STRING = os.getenv('DEV_MONGO_DATABASE_URI')

print(CONNECTION_STRING)

#database names
db_name = "microgrid"
db_name_ess = "microgrid-ess"


# input collection name (same for both DBs)
coll_in_name = "Standard Microgrid"

# output collection names (same for both DBs)
coll_out_name = "de_duplication"
prev_coll_name = "de_duplication_prev"
coll_to_prev = "de_duplication"

#key field (same for both DBs)
key_field = "extKey"

#establish connections
client = MongoClient(CONNECTION_STRING)
db = client[db_name]
db_ess = client[db_name_ess]

#Save curr collection to prev (since process will overwrite curr)
check = list(db[coll_to_prev].aggregate([{'$out': prev_coll_name}]))
check = list(db_ess[coll_to_prev].aggregate([{'$out': prev_coll_name}]))


# =============================================================================
# STEP 1: Microgrid key replacement (use village)
# =============================================================================

mg_pipeline = [
    {
        '$match':  { 'time_stamp': { '$gt': 1620259200 } } #2021-05-06: 1620259200, MAs recent post
    },
    {
        '$sort':  { 'extKey': 1, 'time_stamp': 1 }
    },
    {
        '$group':  {
            '_id': '$extKey',
            'extKey' : { '$last' : '$extKey'},
            'averageAnnualSolarInsolation' : { '$last' : '$averageAnnualSolarInsolation'},
            'baseLoadKw' : { '$last' : '$baseLoadKw'},
            'capacityKw' : { '$last' : '$capacityKw'},
            'cityName' : { '$last' : '$cityName'},
            'coordinates' : { '$last' : '$coordinates'},
            'events' : { '$last' : '$events'},
            'installationDate' : { '$last' : '$installationDate'},
            'managers' : { '$last' : '$managers'},
            'microgridHourlys' : { '$last' : '$microgridHourlys'},
            'rco' : { '$last' : '$rco'},
            'rto' : { '$last' : '$rto'},
            'storageKwh' : { '$last' : '$storageKwh'},
            'villageName' : { '$last' : '$villageName'},
            'provinceName' : { '$last' : '$provinceName'},
            'time_stamp' : { '$last' : '$time_stamp'}
            }
    },
    {
        '$project': {
            "rawExtKey":"$extKey",
            key_field: {'$concat': ["$villageName", "_village"]},
            "averageAnnualSolarInsolation": 1,
            "baseLoadKw": 1,
            "capacityKw": 1,
            "cityName": 1,
            "coordinates": 1,
            "events": 1,
            "installationDate": 1,
            "managers": 1,
            "microgridHourlys": 1,
            "rco": 1,
            "rto": 1,
            "storageKwh": 1,
            "villageName": 1,
            "provinceName": 1,
            "time_stamp": 1
        }
    },
    {
        '$out': coll_out_name
    }
]

db = client[db_name]
db[coll_in_name].aggregate(mg_pipeline)


# =============================================================================
# STEP 2: ESS key replacement (use customer extKey)
# =============================================================================

ess_pipeline = [
    {
        '$match':  { 'time_stamp': { '$gt': 1620259200 } } #2021-05-06: 1620259200, MAs recent post
    },
    {
        '$sort':  { 'extKey': 1, 'time_stamp': 1 }
    },
    {
        '$group':  {
            '_id': '$extKey',
            'extKey' : { '$last' : '$extKey'},       
            'time_stamp' : { '$last' : '$time_stamp'},
            'connectionDate' : { '$last' : '$connectionDate'},
            'paymentStatus' : { '$last' : '$paymentStatus'},
            'productUse' : { '$last' : '$productUse'},
            'customer' : { '$last' : '$customer'},
            'whTransactions' : { '$last' : '$whTransactions'},
            'microgrid' : { '$last' : '$microgrid'}            
            }
    },
    {
        '$project': {
            "rawExtKey":"$extKey",
            key_field: {'$concat': ["$customer.extKey", "_customer"]},
            "customer":1,
            "beneficiary":1,
            "microgrid": {
                "rawExtKey": "$microgrid.extKey",
                key_field: {'$concat': ["$microgrid.nameVillage", "_village"]},
                "nameProvince":"$microgrid.nameProvince",
                "nameCity":"$microgrid.nameCity",
                "nameVillage":"$microgrid.nameVillage",
                "textCoordinates":"$microgrid.textCoordinates",
                "managers":"$microgrid.managers",
                "dtInstallation":"$microgrid.dtInstallation",
                "nbrAvgSolarInsolationAnnual":"$microgrid.nbrAvgSolarInsolationAnnual",
                "nbrBaseLoadKw":"$microgrid.nbrBaseLoadKw",
                "nbrCapacityKw":"$microgrid.nbrCapacityKw",
                "nbrStorageKwh":"$microgrid.nbrStorageKwh",
                "microgridHourlys":"$microgrid.microgridHourlys",
                "partyOperations":"$microgrid.partyOperations"
            },
            "connectionDate":1,
            "paymentStatus":1,
            "productUse":1,
            "subProductUse":1,
            "appliances":1,
            "whTransactions":1,
            "events":1
        }
    },
     {
        '$out': coll_out_name
    }   
]



db_ess[coll_in_name].aggregate(ess_pipeline, allowDiskUse=True)


# =============================================================================
# STEP 3: Dump to JSON and post to INTG environment
# =============================================================================

# For new, do manually from mongo client


