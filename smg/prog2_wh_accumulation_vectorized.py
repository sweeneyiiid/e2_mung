# -*- coding: utf-8 -*-
"""
SMG Customter Wh calculation, vectorized 

 - Input: re-keyed customer/purchase level data 
 - Output: data with Wh by customer and purhcase (for flattening)

Created on Wed Apr  6 10:26:19 2022

@author: DanielSweeney
"""

import pymongo

# =============================================================================
# comment out for dev work if you dont have admin access to your machine
import os
from dotenv import load_dotenv, find_dotenv
# =============================================================================

# =============================================================================
# Program setup
# =============================================================================

# =============================================================================
# use for dev work if you dont have admin access to your machine
# DEV_MONGO_DATABASE_URI = "mongodb+srv://mongo_admin:Test1ng4M*ng0@cluster0.m8t1k.mongodb.net/microgrid?retryWrites=true&w=majority"
# client = pymongo.MongoClient(DEV_MONGO_DATABASE_URI)
# =============================================================================

# =============================================================================
# use for PROD on EC2, or for dev if you have admin access to your machine
#   DEV_MONGO_DATABASE_URI for dev and PROD_MONGO_DATABASE_URI for documentDB
load_dotenv(find_dotenv())
CONNECTION_STRING = os.getenv('PROD_MONGO_DATABASE_URI')
client = pymongo.MongoClient(CONNECTION_STRING)
# =============================================================================

#database name
db_name = "microgrid-ess"

#input/output collection names
coll_name = "de_duplication"

out_coll_name = "wh_accumulation"

db = client[db_name]


# update backup copy with last run
check = list(db[out_coll_name].aggregate([{'$out': "prev_" + out_coll_name}]))


# =============================================================================
# Main pipeline
# =============================================================================

# basic pipeline setup
pipeline = [
    
    # De-duped already in program 1 

        
    # Get unique record at parent level for each transaction within parent record
    #   https://docs.mongodb.com/manual/reference/operator/aggregation/unwind/
    {
        '$unwind':'$whTransactions'
    }
]


# Create Wh Available times from strings
#   https://stackoverflow.com/questions/15780415/how-can-i-store-time-of-day-in-mongodb-as-a-string-give-arbitrary-year-month-d

wh_pipeline = []
    
for i0 in range(5):

    #socket is indexed starting at 1
    i=i0+1
    
    
    #new minute calculation for each socket
    min_pipeline=[]
    
#{ $convert: { input: <expression>, to: "double" } }

    #for each start/stop time within socket
    for j in range(5):
        min_pipeline.append(
            {
                '$subtract':[
                    {
                        '$dateFromString':{ 
                                'dateString':{'$concat':['1970-01-01 ','$whTransactions.socket'+str(i)+'Stop'+str(j)]},
                                'format': '%Y-%m-%d %H%M' 
                        }
                        
                    },
                    {
                        '$dateFromString':{ 
                                'dateString':{'$concat':['1970-01-01 ','$whTransactions.socket'+str(i)+'Start'+str(j)]},
                                'format': '%Y-%m-%d %H%M' 
                        }
                        
                    }
                ]
            }
        )
        # END OF j LOOP
    
    wh_pipeline.append(                                                        
        {
            '$multiply':[
                {
                    '$divide':[{'$sum': min_pipeline}, 3600000] #convert diffs in milliseconds to hours
                },
                {
                    '$convert':{
                        'input':'$whTransactions.nbrCentaAmpLimit'+str(i),
                        'to':'double',
                        'onError':0,
                        'onNull':0
                    }
                },
                2.3 #voltage / 100 (since we are using centaAmps)
            ]
        }
    )
    # END OF i LOOP


#add Wh pipeline to main pipeline and print
pipeline.append({'$addFields':{'whSum':{'$add':wh_pipeline}}})
pipeline.append({'$out': out_coll_name})


#pipeline.append({ '$limit':10 })
check_data = list(db[coll_name].aggregate(pipeline))

