# -*- coding: utf-8 -*-
"""
Create SMG cust Wh by day in LOOP
 - this is probably not the best way to do this
 - but with a small record set, maybe ok


Created on Thu Sep 10 12:15:23 2020

@author: DanielSweeney
"""
import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient


import json #not sure if I will need this anymore
import pandas as pd
import numpy as np


# =============================================================================
# STEP 0: Basic setup and connect
# =============================================================================

#IMPORTANT: the three variables below are the ones to be changed
out_path_exhibit = './data/smg_monitoring_20220620.csv'
per_start = pd.to_datetime('2022-03-31')
per_end = pd.to_datetime('2022-07-01')


load_dotenv(find_dotenv())

# use DEV_MONGO_DATABASE_URI for dev and PROD_MONGO_DATABASE_URI for documentDB
CONNECTION_STRING = os.getenv('PROD_MONGO_DATABASE_URI')

client = MongoClient(CONNECTION_STRING)

#filter to Kampekete
MG_FILTER = '128100'

#database name
db_name_ess = "microgrid-ess"

#input collection name
coll_in_name = "wh_flatten"


# =============================================================================
# Establish cursor
# =============================================================================

#https://stackoverflow.com/questions/28968660/how-to-convert-a-pymongo-cursor-cursor-into-a-dict
#something like:
hist_raw = client[db_name_ess][coll_in_name].find()#.limit(100)


# =============================================================================
# Main bit - Break out by day and format for read into pandas
# =============================================================================

list_for_pd = []
check_start_dt = []
except_flag = 0

for rec in hist_raw:
    
    try:
        curr_days = int(rec['nbrDaysPurchased'])
        curr_dt_start = pd.to_datetime(rec['dtStart'])
        
        check_start_dt.append(curr_dt_start)
        
        curr_cust = rec['custKey']
        curr_use = rec['ess_type']
        curr_mg_key = rec['microgrid_key']
        
        curr_wh_per_day = float(rec['whSum']) #/ curr_days (commented out because vectorized version doesnt use days)
    except:
        except_flag += 1
        curr_wh_per_day = 0
    
    try:
        for i in range(curr_days):
            list_for_pd.append({'cust':curr_cust, 
                                'ess_type':curr_use,
                                'mg_key':curr_mg_key,
                                'active_date': curr_dt_start + pd.DateOffset(i),
                                'wh_available': curr_wh_per_day,})
    except:
        list_for_pd.append({'cust':0, 
                            'ess_type':0,
                            'mg_key':0,
                            'active_date': per_start,
                            'wh_available': 0,})
    

#hist_raw[0]
#3177.45/5

print(max(check_start_dt))
#Timestamp('2020-08-12 00:00:00')



# =============================================================================
# Read into Pandas and do quick summarization for final excel exhibits
# =============================================================================

df_by_day = pd.DataFrame(list_for_pd)
df_by_day.shape

#fill missing ess type values with Household
df_by_day['ess_type'].fillna('Household', inplace=True)

df_by_day_dedup = df_by_day.groupby(['cust', 'ess_type', 'mg_key','active_date'])['wh_available'].sum().reset_index()

# =============================================================================
# for troubleshooting
#df_by_day_dedup = df_by_day.groupby(['cust', 'ess_type', 'active_date']).agg(['sum', 'count']).reset_index()
# =============================================================================
df_by_day_dedup['active_flag'] = 1*(df_by_day_dedup.wh_available > 0)

df_3mo = df_by_day_dedup.loc[np.logical_and(df_by_day_dedup.active_date > per_start,
                                df_by_day_dedup.active_date < per_end),:]
#df_3mo.shape

df_sumry = df_3mo.groupby(['cust', 'ess_type','mg_key'])['wh_available', 'active_flag'].sum().reset_index()

df_sumry.to_csv(out_path_exhibit, index=False)



# =============================================================================
#  Calc quasi-defaults (inactive customers)
# =============================================================================

# in dataset but not in active dataset

df_check = df_by_day_dedup.loc[df_by_day_dedup.mg_key != '128100',:].copy()

print(len(pd.unique(df_check.cust)))
print(len(pd.unique(df_by_day_dedup.cust)))

# aws s3 cp smg_monitoring_20220519.csv s3://microgrid-data-upload/smg_monitoring_20220519.csv

