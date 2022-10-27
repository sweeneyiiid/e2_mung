# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 14:09:21 2021

NOTE: execute from: C:/Users\reeep\OneDrive\Desktop\e2_cleanup\orig_clean\e2_mung\rea\sparkmeter

@author: DanielSweeney

    curl --location --request GET 'https://SITE.sparkmeter.cloud/api/v0/system-info' \
    --header 'Content-Type: application/json' \
    --header 'Authentication-Token: wrong_authentication_token'

Stack Overflow support:
    
    https://stackoverflow.com/questions/25491090/how-to-use-python-to-execute-a-curl-command/48005899

"""

from non_git import config 

import requests
import json #API is JSON

import pandas as pd

# =============================================================================
# Step 1: get sites
# =============================================================================

token_str = config.SM_TOKEN

sites_url = config.SM_ENDPOINT

spark_headers = {"Content-Type": "application/json","Authentication-Token":token_str}

sites_response = requests.get(url=sites_url+"system-info", headers=spark_headers)
sites_json = json.loads(sites_response.text)

sites_json




# =============================================================================
# Step 2: List meter models
# 'http://sparkapp-staging.spk.io:5010/api/v0/meters/models'
# =============================================================================


sites_response = requests.get(url=sites_url+"meters/models", headers=spark_headers)
sites_json = json.loads(sites_response.text)

sites_json


# =============================================================================
# Step 2: List customers
# =============================================================================

models_url = 'http://sparkapp-staging.spk.io:5010/api/v0/customers'

sites_response = requests.get(url=sites_url+"customers", headers=spark_headers)
sites_json = json.loads(sites_response.text)

sites_json.keys()

sites_json['customers'][0]


### Step 2.1: get specific customer
#first customer has system serial number: SM60R-07-0002334E

cust_url = 'customers?meter_serial=SM60R-07-0002334E'

sites_response = requests.get(url=sites_url+cust_url, headers=spark_headers)
sites_json = json.loads(sites_response.text)

sites_json

# Works, but is this any more detailed than pulling all customers?

# Next steps: how easy is this to throw into pandas? also, do I need to do something similar to victron de-duping?





# =============================================================================
# Step 2: List customers
# =============================================================================

models_url = 'http://sparkapp-staging.spk.io:5010/api/v0/totalizers'

sites_response = requests.get(url=models_url, headers=spark_headers)
sites_json = json.loads(sites_response.text)

sites_json



models_url = 'http://sparkapp-staging.spk.io:5010/api/v0/totalizers'

sites_response = requests.get(url=models_url, headers=spark_headers)
sites_json = json.loads(sites_response.text)

sites_json



















#need to break this down into the components so I can modify them later
main_url_base = 'https://vrmapi.victronenergy.com/v2/installations/95394/stats?'


#in epoch format, make sure they are both on the top of the hour
start_param = 1638964800
end_param = 1639051200


#the KPIs are the key part, but also probably wont change much once set
kpi_params = ["bs", # Battery Storage % charged
              "Bc", # Battery to consumers
              "Pb", # PV to battery
              "Pc"] # PV to consumers

#these tow probably wont change much, but are technically parameters
interval_param = "hours"
type_param = "custom"

#integrate parameters into URL
main_url = main_url_base + 'type=' + type_param
main_url = main_url + '&start=' + str(start_param)
main_url = main_url + '&end=' + str(end_param)
main_url = main_url + '&interval=' + interval_param
for i in kpi_params:
    main_url = main_url + '&attributeCodes[]=' + i


# setup header with token
main_header = {"X-Authorization": "Bearer "+token_str}

#make query and extract response into JSON
main_response = requests.get(url=main_url, headers=main_header)
main_json = json.loads(main_response.text)

#ok, looks good, but remember there may not be all metrics for all hours (e.g. - not always charging battery)

# =============================================================================
# Step 3: load data to Mongo
# =============================================================================


print(main_json)


# right now dev only, leave prod to Saminu

#first convert it to BSON
#main_bson = bson.encode(main_json)

client = pymongo.MongoClient(DEV_MONGO_DATABASE_URI)

#database name
db_name = "victron"

#input collection name
coll_name = "sandbox"

client[db_name][coll_name].insert_one(main_json)


# # =============================================================================
# # Step 4: process data for visualization / analysis
# # =============================================================================

# #I think basically want 1 obs for every hour
# #then come back to an SSOT issue, so I need to think about that either way

# #for now throw it in excel and see what it looks like

# #battery to consumers
# ds_bc = pd.DataFrame(main_json['records']['Bc'], columns=['timestamp', 'Bc'])

# #PV to consumers
# ds_pc = pd.DataFrame(main_json['records']['Pc'], columns=['timestamp', 'Pc'])

# #PV to battery
# ds_pb = pd.DataFrame(main_json['records']['Pb'], columns=['timestamp', 'Pb'])

# #battery storage (% charged)
# ds_bs = pd.DataFrame(main_json['records']['bs'], columns=['timestamp', 'bs_mean', 'bs_min', 'bs_max'])
