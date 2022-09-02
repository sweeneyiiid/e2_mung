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

out_path_ssot = './kampekete_smg_ssot_20220527.csv'
out_path_exhibit = './kampekete_exhibit_20220527.csv'

# per_start = pd.to_datetime('2021-07-31')
# per_end = pd.to_datetime('2021-11-01')


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


for rec in hist_raw: # for i,rec in enumerate(hist_raw):
    
    # if i % 1000 == 0:
        # print(i)
    
    curr_days = int(rec['nbrDaysPurchased'])
    curr_dt_start = pd.to_datetime(rec['dtStart'])
    
    check_start_dt.append(curr_dt_start)
    
    curr_cust = rec['custKey']
    curr_use = rec['ess_type']
    curr_mg_key = rec['microgrid_key']
    try:
        curr_wh_per_day = float(rec['whSum']) / curr_days
    except:
        except_flag += 1
        curr_wh_per_day = 0
    
    for i in range(curr_days):
        list_for_pd.append({'cust':curr_cust, 
                            'ess_type':curr_use,
                            'mg_key':curr_mg_key,
                            'active_date': curr_dt_start + pd.DateOffset(i),
                            'wh_available': curr_wh_per_day,})

print('maximum start date: \n')
print(str(max(check_start_dt)))



# =============================================================================
# Read into Pandas and establish SSOT baseline (drop-replace)
# =============================================================================

df_by_day = pd.DataFrame(list_for_pd)
# df_by_day.shape

#fill missing ess type values with 
df_by_day['ess_type'].fillna('Unknown', inplace=True)

df_by_day_dedup = df_by_day.groupby(['cust', 'ess_type', 'mg_key','active_date'])['wh_available'].sum().reset_index()

#filter to Kampekete
df_ssot = df_by_day_dedup.loc[df_by_day_dedup.mg_key == MG_FILTER,:].copy()

# TO DO: add drop (or archive) previous day, also figure out how to write directly to S3
df_ssot.to_csv(out_path_ssot, index=False)


# =============================================================================
# Summarize SSOT for dashboard exhibit
# =============================================================================
#NOTE: this may end up moving to a separate programme for dashboard prep


df_ssot['num_consumers'] = 1*(df_ssot.wh_available > 0)

df_sumry = df_ssot.groupby('active_date')[['wh_available', 'num_consumers']].sum().reset_index()

df_sumry.to_csv(out_path_exhibit, index=False)

# aws s3 cp kampekete_smg_ssot_20220412_X.csv s3://microgrid-data-upload/kampekete_smg_ssot_20220412_X.csv
# aws s3 cp kampekete_exhibit_20220412_X.csv s3://microgrid-data-upload/kampekete_exhibit_20220412_X.csv


# =============================================================================
#  Calc tier? (maybe not)
# =============================================================================


# tier_cutter = [0,20,80,190,550,3000,8000,99999]
# df_sumry['tier'] = pd.cut(df_sumry.wh_day_active,bins=tier_cutter,right=False,labels=False)


