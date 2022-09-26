# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 14:09:21 2021

@author: DanielSweeney

POST token request: 
    
    curl --location --request POST 'https://vrmapi.victronenergy.com/v2/auth/login' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "username": "dlswee@gmail.com",
        "password": "xxx"
        }'

GET query:

    curl --location -g --request GET 'https://vrmapi.victronenergy.com/v2/installations/95394/stats?{params} \
    --header 'X-Authorization: Bearer {token}

Stack Overflow support:
    
    https://stackoverflow.com/questions/25491090/how-to-use-python-to-execute-a-curl-command/48005899

"""

import requests
import json #API is JSON

import pandas as pd

import pymongo
#import bson #But Mongo is BSON
#from app.config import ConfigVictron

#DEV_MONGO_DATABASE_URI = "mongodb+srv://admin:1llml8odsy4D5Px4@cluster0.ok5iq.mongodb.net/microgrid?retryWrites=true&w=majority"

# =============================================================================
# Step 1: get token for request
# =============================================================================

# token_url = "https://vrmapi.victronenergy.com/v2/auth/login"

# #for some reason curl doesn't like this passed as a dict
# token_body = '{"username":"'+token_user+'","password":"'+token_pass+'"}'

token_user = "dlswee@gmail.com"
token_pass = ""

token_body = '{"username":"'+token_user+'","password":"'+token_pass+'"}'

token_url = "https://vrmapi.victronenergy.com/v2/auth/login"


token_response = requests.post(url=token_url, data=token_body)
token_json = json.loads(token_response.text)


#type(token_json['token'])
token_str = token_json['token']
token_num = str(token_json['idUser'])




# =============================================================================
# Step 2: get sites (only need to run once to get site ID)
# =============================================================================


# https://vrmapi.victronenergy.com/v2/users/{idUser}/installations

# #sites_url = 'https://vrmapi.victronenergy.com/v2/users/'+token_num+'/installations?extended=1'
# sites_url = 'https://vrmapi.victronenergy.com/v2/users/'+token_num+'/installations'

# # setup header with token
# main_header = {"X-Authorization": "Bearer "+token_str}

# #make query and extract response into JSON
# main_response = requests.get(url=sites_url, headers=main_header)
# main_json = json.loads(main_response.text)

# ### PROBLEM: Chaba is a shared installation, I don't have access to it in the API
# main_json['records'][0]


# chaba is 'idSite': 125796






# =============================================================================
# Step 2: get a couple hours worth of data to check against VRM 
# =============================================================================




#need to break this down into the components so I can modify them later
main_url_base = 'https://vrmapi.victronenergy.com/v2/installations/125796/stats?'


#in epoch format, make sure they are both on the top of the hour
start_param = 1663826400 #2022-09-22 0600Z
end_param = 1663851600 #2022-09-22 1300Z


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


check_data = main_json['records']

def datasetter(js, name):
    x = pd.DataFrame(js[name])
    x.columns = ['epoch', name]

# non_standard metric
bs_data = pd.DataFrame(check_data['bs'])
bs_data.rename(['epoch', 'avg_bat', 'min_bat', 'max_bat'])

bs_data.columns = ['epoch', 'avg_bat', 'min_bat', 'max_bat']

pb_data = datasetter(check_data, 'Pb')
pb_data = datasetter(check_data, 'Pb')
pb_data = datasetter(check_data, 'Pb')




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
