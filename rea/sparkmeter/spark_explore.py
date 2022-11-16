# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 14:09:21 2021

NOTE: execute from: C:/Users\reeep\OneDrive\Desktop\e2_cleanup\orig_clean\e2_mung\rea\sparkmeter
      or wherever you have access to the config file with the credentials for REA sparkmeters

@author: DanielSweeney

"""

from non_git import config 

import requests
import json #API is JSON

import pandas as pd

# =============================================================================
# Step 0: set up variables to connect
# =============================================================================

#get credentials from non-git file
token_str = config.SM_TOKEN
sites_url = config.SM_ENDPOINT

#set up credentials within request
spark_headers = {"Content-Type": "application/json","Authentication-Token":token_str}


# =============================================================================
# Step 1: get sites - basic data, not that interesting
# =============================================================================

# sites_response = requests.get(url=sites_url+"system-info", headers=spark_headers)
# sites_json = json.loads(sites_response.text)

# sites_json



# =============================================================================
# Step 2: List customers - includes current readings
# =============================================================================

#models_url = 'http://sparkapp-staging.spk.io:5010/api/v0/customers'

cust_response = requests.get(url=sites_url+"customers", headers=spark_headers)
cust_json = json.loads(cust_response.text)

# #quick check on response
# cust_json.keys()
# cust_json['customers'][0]['meters'][0]

#what we really care about is actually meters, which are nested in customers

meters = []
for i in cust_json['customers']:
    for j in i['meters']:
        meters.append(j)

meters_df = pd.DataFrame(meters)

# meters_df.to_csv('./non_git/data/meters_202211031016cet.dat', index=False, sep='\t')









# #So comes out ok, but appears to be more detail in ground and meter sub-jsons

# len(sites_json['customers'][0]['meters'])


# ### Step 2.1: get specific customer
# #first customer has system serial number: SM60R-07-0002334E

# cust_url = 'customers?meter_serial=SM60R-07-0002334E'

# sites_response = requests.get(url=sites_url+cust_url, headers=spark_headers)
# sites_json = json.loads(sites_response.text)

# sites_json

# # Works, but is this any more detailed than pulling all customers?

# # Next steps: how easy is this to throw into pandas? also, do I need to do something similar to victron de-duping?





# # =============================================================================
# # Step 2: List customers
# # =============================================================================

# models_url = 'http://sparkapp-staging.spk.io:5010/api/v0/totalizers'

# sites_response = requests.get(url=models_url, headers=spark_headers)
# sites_json = json.loads(sites_response.text)

# sites_json



# models_url = 'http://sparkapp-staging.spk.io:5010/api/v0/totalizers'

# sites_response = requests.get(url=models_url, headers=spark_headers)
# sites_json = json.loads(sites_response.text)

# sites_json










