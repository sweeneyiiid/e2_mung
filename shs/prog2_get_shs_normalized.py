# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 14:00:00 2022

@author: DanielSweeney
"""

import pandas as pd

shs_in_path = "./data/shs_dump.csv"
pmt_in_path = "./data/pmt_dump.csv"

out_path = "./data/shs_data_asof_"


as_of_str = "2022-02-01"
as_of_dt = pd.to_datetime(as_of_str).date()



# =============================================================================
#  STEP 1: SHS Table
# =============================================================================

shs_raw = pd.read_csv(shs_in_path)

shs_raw['dt_acq'] = pd.to_datetime(shs_raw.acquisitionDate,
                                   format="%Y-%m-%dT%H:%M:%SZ",
                                   errors="coerce").dt.date

shs_raw['paid_off_dt'] = pd.to_datetime(shs_raw.datePaidOff,
                                   format="%Y-%m-%dT%H:%M:%SZ",
                                   errors="coerce").dt.date

shs_raw.rename(columns={'serialNumber':'ser_num',
                        'productId':'product',
                        'downPayment':'down_pmt',
                        'totalFinancedAtTimeOfPurchase':'ttl_fin'},
               inplace=True)
       
droppers = ["_id", "acquisitionDate", "datePaidOff"]
shs_clean = shs_raw.drop(droppers, axis=1)

# for backward compatibility
shs_clean["cust_key"] = "not_needed"       

shs_ready = shs_clean.loc[shs_clean.dt_acq < as_of_dt].copy()

shs_ready['shs_key'] = shs_ready.shs_key.astype('int')


# =============================================================================
#  STEP 2: Payment table
# =============================================================================

pmt_raw = pd.read_csv(pmt_in_path)

pmt_raw.columns


#bad names, just saving time for group by

pmt_raw['max_pmt_dt'] = pd.to_datetime(pmt_raw.dtPayment,
                                   format="%Y-%m-%dT%H:%M:%SZ",
                                   errors="coerce").dt.date


pmt_raw['tot_pmt'] = pmt_raw.amtPayment.astype('int')

pmt_asof = pmt_raw.loc[pmt_raw.max_pmt_dt < as_of_dt].copy()

pmt_sumry = pmt_asof.groupby(['shs_key']).aggregate({'tot_pmt':'sum', 'max_pmt_dt':'max'}).reset_index()


# =============================================================================
#  Step 3: join and print
# =============================================================================

ds_combo = shs_ready.merge(pmt_sumry, how='left', on='shs_key')

#order of columns is important downstream
col_order = ['shs_key',
             'cust_key',
             'dt_acq',
             'product',
             'province',
             'gender',
             'down_pmt',
             'ttl_fin',
             'paid_off_dt',
             'time_stamp',
             'ser_num',
             'tot_pmt',
             'max_pmt_dt']

ds_combo[col_order].to_csv(out_path+as_of_str+'.csv', index=False)




