# -*- coding: utf-8 -*-
"""
Flatten Wh transaction records for ad hoc analysis
Created on Tue Aug  4 10:52:20 2020

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

#database name
db_name_ess = "microgrid-ess"

#input collection name
coll_in_name = "wh_accumulation"


# output collection names (same for both DBs)
coll_out_name = "wh_flatten"
prev_coll_name = "wh_flatten_prev"
coll_to_prev = "wh_flatten"

#establish connection
client = MongoClient(CONNECTION_STRING)
db_ess = client[db_name_ess]

# update backup copy with last run
check = list(db_ess[coll_to_prev].aggregate([{'$out': prev_coll_name}]))


# =============================================================================
# STEP 1: put Wh data in tabular form
# =============================================================================

ess_pipeline = [
    # {
    #     '$limit': 1000
    # },
    {
         '$project': {
                "essKey":"$rawExtKey",
                "custKey": "$customer.extKey",
                "cust_gender" : "$customer.textGender",
                "ess_type" : "$productUse",
                "microgrid_key" :{"$substrCP":["$microgrid.rawExtKey",0,6]},
                "whTransactions":1,
                "whSum":1
             }
    },
    {
        '$project': {
                    "essKey":1,
                    "custKey":1,
                    "cust_gender":1,
                    "ess_type":1, 
                    "microgrid_key":1,
                    'extKey':'$whTransactions.extKey',
                    'dtStart':'$whTransactions.dtStart',
                    'nbrDaysPurchased':'$whTransactions.nbrDaysPurchased',
                    'nbrAmtPaidZmw':'$whTransactions.nbrAmtPaidZmw',
                    'textPaymentStatus':'$whTransactions.textPaymentStatus',
                    'whSum':1
        }
    },
    {
        '$out': coll_out_name
    }   
]


print(list(db_ess[coll_in_name].aggregate(ess_pipeline)))


# =============================================================================
# STEP 3: Dump to JSON and post to INTG environment
# =============================================================================
