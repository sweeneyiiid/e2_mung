# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 14:09:21 2021

@author: DanielSweeney

POST request to get token (last for like an hour, so usually have to grab a new one): 
    
    curl --location --request POST 'https://vrmapi.victronenergy.com/v2/auth/login' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "username": "dlswee@gmail.com",
        "password": "xxx"
        }'

GET request for metrics (once you have your token):

    curl --location -g --request GET 'https://vrmapi.victronenergy.com/v2/installations/95394/stats?{params} \
    --header 'X-Authorization: Bearer {token}

Stack Overflow support:
    
    https://stackoverflow.com/questions/25491090/how-to-use-python-to-execute-a-curl-command/48005899

"""

import requests
import json #API is JSON

import pandas as pd

import sqlite3

# =============================================================================
# Step 1: get token for request
# =============================================================================

# #for some reason curl doesn't like this passed as a dict
# token_body = '{"username":"'+token_user+'","password":"'+token_pass+'"}'

token_user = "dlswee@gmail.com"
token_pass = ""

token_body = '{"username":"'+token_user+'","password":"'+token_pass+'"}'

token_url = "https://vrmapi.victronenergy.com/v2/auth/login"

token_response = requests.post(url=token_url, data=token_body)
token_json = json.loads(token_response.text)

token_str = token_json['token']
token_num = str(token_json['idUser'])

# =============================================================================
# Step 2: get sites (only need to run once to get site ID)
# =============================================================================

# #https://vrmapi.victronenergy.com/v2/users/{idUser}/installations

# #sites_url = 'https://vrmapi.victronenergy.com/v2/users/'+token_num+'/installations?extended=1'
# sites_url = 'https://vrmapi.victronenergy.com/v2/users/'+token_num+'/installations'

# # setup header with token
# main_header = {"X-Authorization": "Bearer "+token_str}

# #make query and extract response into JSON
# main_response = requests.get(url=sites_url, headers=main_header)
# main_json = json.loads(main_response.text)

# main_json['records']

# #chaba is 'idSite': 125796

# =============================================================================
# Step 3: setup SQLite tables for raw-ish data ONLY NEED TO RUN ONCE
# =============================================================================



db_path = "C:/Users/reeep/OneDrive/Desktop/e2_cleanup/esp_db/victron_db.db"

conn = sqlite3.connect(db_path)

# # Base table: battery status (base because record exists for every hour)
# base_table_str = """ CREATE TABLE IF NOT EXISTS base (
#                                         id integer PRIMARY KEY,
#                                         epoch integer,
#                                         avg_bat real,
#                                         min_bat real,
#                                         max_bat real,
#                                         reading_time integer,
#                                         site integer,
#                                         get_time integer
#                                     ); """

# c = conn.cursor()
# c.execute(base_table_str)


# # PV going to battery
# pb_table_str = """ CREATE TABLE IF NOT EXISTS pv_to_battery (
#                                         id integer PRIMARY KEY,
#                                         epoch integer,
#                                         Pb real,
#                                         reading_time integer,
#                                         site integer,
#                                         get_time integer
#                                     ); """

# c = conn.cursor()
# c.execute(pb_table_str)

# # PV going to customers
# pc_table_str = """ CREATE TABLE IF NOT EXISTS pv_to_customer (
#                                         id integer PRIMARY KEY,
#                                         epoch integer,
#                                         Pc real,
#                                         reading_time integer,
#                                         site integer,
#                                         get_time integer
#                                     ); """

# c = conn.cursor()
# c.execute(pc_table_str)


# #Battery going to customers
# bc_table_str = """ CREATE TABLE IF NOT EXISTS battery_to_customer (
#                                         id integer PRIMARY KEY,
#                                         epoch integer,
#                                         Bc real,
#                                         reading_time integer,
#                                         site integer,
#                                         get_time integer
#                                     ); """

# c = conn.cursor()
# c.execute(bc_table_str)





# conn.commit()

# conn.close()




# =============================================================================
# Step 4: get a couple hours worth of data to check against VRM 
# =============================================================================

#site ID from step 2
mg_site = 125796

#need to break this down into the components so I can modify them later
main_url_base = 'https://vrmapi.victronenergy.com/v2/installations/'+str(mg_site)+'/stats?'


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

#record time of get request
GET_TIME = pd.Timestamp.now(tz='utc')

json_data = main_json['records']

def datasetter(js, name, get_ts, mg_id):
    x = pd.DataFrame(js[name])
    x.columns = ['epoch', name]
    x['reading_time'] = pd.to_datetime(x.epoch, unit='ms')
    x['site'] = mg_id
    x['get_time'] = get_ts
    return x

# non_standard metric
bs_data = pd.DataFrame(json_data['bs'])
bs_data.columns = ['epoch', 'avg_bat', 'min_bat', 'max_bat']
bs_data['reading_time'] = pd.to_datetime(bs_data.epoch, unit='ms')
bs_data['site'] = mg_site
bs_data['get_time'] = GET_TIME


pb_data = datasetter(json_data, 'Pb', GET_TIME, mg_site)
pc_data = datasetter(json_data, 'Pc', GET_TIME, mg_site)
bc_data = datasetter(json_data, 'Bc', GET_TIME, mg_site)



# =============================================================================
# Step 5: load data into SQLite 
# =============================================================================

#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

bs_data.to_sql('base', conn, if_exists='append', index=False)

pb_data.to_sql('pv_to_battery', conn, if_exists='append', index=False)
pc_data.to_sql('pv_to_customer', conn, if_exists='append', index=False)
bc_data.to_sql('battery_to_customer', conn, if_exists='append', index=False)


# =============================================================================
# Step 6: get tables with max timestamp
# =============================================================================


base_max_string = """
                     drop table if exists max_base;
                     create table max_base as 
                     select reading_time, avg_bat, max(get_time)
                     from base
                     group by reading_time, avg_bat;
                 """

c = conn.cursor()
c.executescript(base_max_string)

# battery status
base_max_string = """
                     drop table if exists max_base;
                     create table max_base as 
                     select reading_time, avg_bat, max(get_time)
                     from base
                     group by reading_time, avg_bat;
                 """

c = conn.cursor()
c.executescript(base_max_string)

# pv to battery
pb_max_string = """
                     drop table if exists max_pb;
                     create table max_pb as 
                     select reading_time, Pb, max(get_time)
                     from pv_to_battery
                     group by reading_time, Pb;
                 """

c = conn.cursor()
c.executescript(pb_max_string)


# pv to customers
pc_max_string = """
                     drop table if exists max_pc;
                     create table max_pc as 
                     select reading_time, Pc, max(get_time)
                     from pv_to_customer
                     group by reading_time, Pc;
                 """

c = conn.cursor()
c.executescript(pc_max_string)



# battery to customers
pc_max_string = """
                     drop table if exists max_bc;
                     create table max_bc as 
                     select reading_time, Bc, max(get_time)
                     from battery_to_customer
                     group by reading_time, Bc;
                 """

c = conn.cursor()
c.executescript(pc_max_string)



conn.commit()


# =============================================================================
# Step 7: get tables with max timestamp
# =============================================================================

ssot_str = """
drop table if exists ssot;
create table ssot as
select  bs.*
       ,ifnull(pb.pb,0) as pb
       ,ifnull(pc.pc,0) as pc
       ,ifnull(bc.bc,0) as bc
       ,ifnull(pc.pc,0) + ifnull(bc.bc,0) as tot_c
from
    max_base as bs left join max_pb as pb
        on bs.reading_time = pb.reading_time
    left join max_pc as pc
        on bs.reading_time = pc.reading_time
    left join max_bc as bc
        on bs.reading_time = bc.reading_time
"""

c = conn.cursor()
c.executescript(ssot_str)

conn.commit()

# cur = conn.cursor()
# cur.execute("SELECT * FROM ssot")
# rows = cur.fetchall()
# rows[0]


# =============================================================================
# Step 8: read into pandas DF (eventually this should be a separate script)
# =============================================================================


df_ssot = pd.read_sql('select * from ssot', conn, parse_dates=['reading_time', 'get_time'])


conn.close()


