# -*- coding: utf-8 -*-
"""

Assuming we have a good SSOT collection, get it to pandas and then CSV

"""



import pymongo
import pandas as pd

DEV_MONGO_DATABASE_URI = "mongodb+srv://<user>:<password>@cluster0.ok5iq.mongodb.net/microgrid?retryWrites=true&w=majority"

out_path = 'C:/Users/DanielSweeney/Desktop/git_local/edison_lite/prototypes/ssot/actuals/ssot_victron.csv'

# =============================================================================
# Step 1: get data
# =============================================================================


client = pymongo.MongoClient(DEV_MONGO_DATABASE_URI)

#database name
db_name = "victron"

#input collection name
coll_name = "ssot"


json_raw = list(client[db_name][coll_name].find())

ds_raw = pd.DataFrame(json_raw)

# =============================================================================
# step 2: put in format for quicksight
# =============================================================================

# translate reading hour to datetime
ds_raw['reading_hour'] = pd.to_datetime(ds_raw.unix_hour, unit='ms')

# fillna with 0
ds_raw.fillna(0, inplace=True)

# wh_consumed = Bc + Pc
ds_raw['wh_consumed'] = ds_raw.Bc_reading + ds_raw.Pc_reading

# wh_produced = Pb + Pc
ds_raw['wh_produced'] = ds_raw.Pb_reading + ds_raw.Pc_reading

# wh_to_battery = Pb
ds_raw['wh_to_battery'] = ds_raw.Pb_reading

# wh_from_battery
ds_raw['wh_from_battery'] = ds_raw.Bc_reading

#batter_storage %
ds_raw['battery_percent'] = ds_raw.bs_reading

keepers = ['reading_hour', 'wh_consumed', 'wh_produced', 'wh_to_battery', 'wh_from_battery', 'battery_percent']

ds_raw[keepers].to_csv(out_path, index=False)

