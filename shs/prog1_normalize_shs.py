# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:59:10 2022

@author: DanielSweeney
"""

import os
from dotenv import load_dotenv, find_dotenv

import pymongo
import pandas as pd

# =============================================================================
# STEP 0: Basic setup and connect
# =============================================================================

load_dotenv(find_dotenv())

CONNECTION_STRING = os.getenv('PROD_MONGO_DATABASE_URI')

client = pymongo.MongoClient(CONNECTION_STRING)

shs_out_path = './data/shs_dump.csv'
pmt_out_path = './data/pmt_dump.csv'

#database name
db_name = "archive"
coll_name = "shs"

# =============================================================================
# STEP 1: SHS dataset
# =============================================================================

shs_pipe = [
    {
        '$sort':  { 'extKey': 1, 'time_stamp': 1 }
    },
    {
        '$group':  {
            '_id' : '$extKey',
            'shs_key' : {'$last' : '$extKey'},
            'serialNumber' : {'$last' : '$serialNumber'},
            'acquisitionDate' : {'$last' : '$acquisitionDate'},
            'datePaidOff' : {'$last' : '$datePaidOff'}, #TO DO: ideally this would be min among non-null
            'productId' : {'$last' : '$productId'},
            'gender' : {'$last' : '$customer.textGender'},
            'province' : {'$last' : '$customer.nameProvince'},
            'downPayment' : {'$last' : '$downPayment'},
            'totalFinancedAtTimeOfPurchase' : {'$last' : '$totalFinancedAtTimeOfPurchase'},
            'time_stamp' : {'$last' : '$time_stamp'}
        }
    },
]

shs_json = list(client[db_name][coll_name].aggregate(shs_pipe))

shs_ds = pd.DataFrame(shs_json)

shs_ds.to_csv(shs_out_path, index=False)


# =============================================================================
# STEP 2: Payment ds
# =============================================================================


pmt_pipe1 = [
        
    #can't really sort before unwind, but I worry what that will do to performance
    {
        '$unwind':'$paygTransactions'
    },
    {
        '$addFields':{'pmt_key':'$paygTransactions.extKey'}
    },
    {
        '$project': {
            "_id":0,
            "extKey":1,
            "pmt_key":1,
            "paygTransactions": 1,
            "time_stamp": 1
        }
    },
    {
        '$out':'payments'
    }
]

list(client[db_name][coll_name].aggregate(pmt_pipe1))

resp = client[db_name]['payments'].create_index(
    [
        ("pmt_key", 1),
        ("time_stamp", 1)
    ]
)

print ("index response:", resp)

pmt_pipe2 = [
    # IF sort craps out, come back to here and drop into a new collection
    # then add an index to that collection and run the rest of the pipeline on it
    # (it did crap out, see above steps)
    {
        '$sort':  { 'pmt_key': 1, 'time_stamp': 1 }
    },
    {
        '$group':  {
            '_id' : '$pmt_key',
            'pmt_key' : {'$last' : '$pmt_key'},
            'amtPayment' : {'$last' : '$paygTransactions.amtPayment'},
            'dtPayment' : {'$last' : '$paygTransactions.dtPayment'},
            'shs_key' : {'$last' : '$extKey'},
            'time_stamp' : {'$last' : '$time_stamp'}
        }
    }      
]


pmt_json = list(client[db_name]['payments'].aggregate(pmt_pipe2, allowDiskUse=True))

pmt_ds = pd.DataFrame(pmt_json)

pmt_ds.to_csv(pmt_out_path, index=False)






