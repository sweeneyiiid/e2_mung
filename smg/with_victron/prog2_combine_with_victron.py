# -*- coding: utf-8 -*-
"""
COMBINE VICTRON AND SMG DATA INTO MAIN SSOT

Created on Wed Mar 30 12:46:03 2022

@author: DanielSweeney
"""

import pandas as pd


base_path = 'C:/Users/DanielSweeney/Desktop/git_local/edison_lite/prototypes/ssot/actuals/'
in_victron_file = 'ssot_victron.csv'
in_smg_file = 'kampekete_exhibit_20220527.csv'
out_ssot_file = 'ssot_main.csv'



#read in Victron and SMG data
ds_smg = pd.read_csv(base_path+in_smg_file, parse_dates=['active_date'])
ds_smg['reading_date'] = ds_smg.active_date.dt.date


ds_victron = pd.read_csv(base_path+in_victron_file, parse_dates=['reading_hour'])

# Summarize Victron data by day
ds_victron['reading_date'] = ds_victron.reading_hour.dt.date

ds_victron_daily = ds_victron.groupby('reading_date')['wh_consumed'].sum().reset_index()


# Join together and dump to CSV
ds_ssot = ds_victron_daily.merge(ds_smg.drop('active_date', axis=1), how='left', on='reading_date')

ds_ssot['kwh_purchased'] = ds_ssot.wh_available / 1000

ds_ssot.rename({'wh_consumed':'kwh_consumed'})
ds_ssot.drop('wh_available', axis=1, inplace=True)

ds_ssot.to_csv(base_path+out_ssot_file, index=False)

