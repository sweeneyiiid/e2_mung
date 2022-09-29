# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 12:39:16 2022

@author: reeep
"""

import requests
import json #API is JSON
import pandas as pd
import sqlite3

def setup_db(conn):
    """
    Function to set up Schema, ONLY NEEDS TO BE RUN ONCE

    Parameters
    ----------
    conn : SQLite connection.

    Returns
    -------
    None.

    """


    # Base table: battery status (base because record exists for every hour)
    base_table_str = """ CREATE TABLE IF NOT EXISTS base (
                                            id integer PRIMARY KEY,
                                            epoch integer,
                                            avg_bat real,
                                            min_bat real,
                                            max_bat real,
                                            reading_time integer,
                                            site integer,
                                            get_time integer
                                        ); """
    
    c = conn.cursor()
    c.execute(base_table_str)
    
    
    # PV going to battery
    pb_table_str = """ CREATE TABLE IF NOT EXISTS pv_to_battery (
                                            id integer PRIMARY KEY,
                                            epoch integer,
                                            Pb real,
                                            reading_time integer,
                                            site integer,
                                            get_time integer
                                        ); """
    
    c = conn.cursor()
    c.execute(pb_table_str)
    
    # PV going to customers
    pc_table_str = """ CREATE TABLE IF NOT EXISTS pv_to_customer (
                                            id integer PRIMARY KEY,
                                            epoch integer,
                                            Pc real,
                                            reading_time integer,
                                            site integer,
                                            get_time integer
                                        ); """
    
    c = conn.cursor()
    c.execute(pc_table_str)
    
    
    #Battery going to customers
    bc_table_str = """ CREATE TABLE IF NOT EXISTS battery_to_customer (
                                            id integer PRIMARY KEY,
                                            epoch integer,
                                            Bc real,
                                            reading_time integer,
                                            site integer,
                                            get_time integer
                                        ); """
    
    c = conn.cursor()
    c.execute(bc_table_str)
    
    conn.commit()

    return None



def get_token(token_user, token_pass):
    """
    Function to get victron API parameters, including token and user id

    Parameters
    ----------
    token_user : string with email address of VRM user.
    pw : string with VRM password.

    Returns
    -------
    dict:
        {
            token: Victron API token (string) to be used in GET requests (lasts about an hour),
            user_id: permanent user id (string) for certain API calls
        }

    """

    token_body = '{"username":"'+token_user+'","password":"'+token_pass+'"}'

    token_url = "https://vrmapi.victronenergy.com/v2/auth/login"

    token_response = requests.post(url=token_url, data=token_body)
    token_json = json.loads(token_response.text)

    token_str = token_json['token']
    token_num = str(token_json['idUser'])
    
    return {'token':token_str, 'user_id':token_num}

def get_basics(token, user_id):
    """
    Function to get summary of all sites accessible to user, ONLY NEEDS TO BE RUN ONCE

    Parameters
    ----------
    token : string with victron API token
    user_id : string with victron API user id

    Returns
    -------
    JSON with minigrid site information for all minigrids on user account, 
    including site ID for future queries and lat/lon

    """
    sites_url = 'https://vrmapi.victronenergy.com/v2/users/'+user_id+'/installations?extended=1'
    
    # setup header with token
    main_header = {"X-Authorization": "Bearer "+token}
    
    #make query and extract response into JSON
    main_response = requests.get(url=sites_url, headers=main_header)
    main_json = json.loads(main_response.text)
    
    return main_json['records']




def get_raw(token, site, conn, start, stop):
    """
    Function to pull victron metrics for a given site and store in SQLite table
        - currently metrics are hard-coded as [bs, Bc, Pb, Pc]
        - interval is coded to hourly (most granular available)

    Parameters
    ----------
    token : user token.
    site : id of site to pull data from.
    conn : DB connection to store data.
    start : epoch start time of data to be pulled.
    stop : epoch stop time of data to be pulled.  NOTE: must be less than a month

    Returns
    -------
    None.

    """
    
    #need to break this down into the components so I can modify them later
    main_url_base = 'https://vrmapi.victronenergy.com/v2/installations/'+str(site)+'/stats?'
    
    
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
    main_url = main_url + '&start=' + str(start)
    main_url = main_url + '&end=' + str(stop)
    main_url = main_url + '&interval=' + interval_param
    for i in kpi_params:
        main_url = main_url + '&attributeCodes[]=' + i
    
    
    # setup header with token
    main_header = {"X-Authorization": "Bearer "+token}
    
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
    try:
        # non_standard metric
        bs_data = pd.DataFrame(json_data['bs'])
        bs_data.columns = ['epoch', 'avg_bat', 'min_bat', 'max_bat']
        bs_data['reading_time'] = pd.to_datetime(bs_data.epoch, unit='ms')
        bs_data['site'] = site
        bs_data['get_time'] = GET_TIME


        pb_data = datasetter(json_data, 'Pb', GET_TIME, site)
        pc_data = datasetter(json_data, 'Pc', GET_TIME, site)
        bc_data = datasetter(json_data, 'Bc', GET_TIME, site)

        bs_data.to_sql('base', conn, if_exists='append', index=False)
        
        pb_data.to_sql('pv_to_battery', conn, if_exists='append', index=False)
        pc_data.to_sql('pv_to_customer', conn, if_exists='append', index=False)
        bc_data.to_sql('battery_to_customer', conn, if_exists='append', index=False)
    except:
        print('missing metric data in call, not loaded')
    
    return None

def update_ssot(conn):
    """
    Function to update SSOT (metrics table) once additional raw data is loaded

    Parameters
    ----------
    conn : Connection to SQLite.

    Returns
    -------
    None.

    """
    
    # battery status
    base_max_string = """
                         drop table if exists max_base;
                         create table max_base as 
                         select site, reading_time, max(get_time) as max_ts
                         from base
                         group by site, reading_time;
                     """
    
    c = conn.cursor()
    c.executescript(base_max_string)
    
    # pv to battery
    pb_max_string = """
                         drop table if exists max_pb;
                         create table max_pb as 
                         select site, reading_time, max(get_time) as max_ts
                         from pv_to_battery
                         group by site, reading_time;
                     """
    
    c = conn.cursor()
    c.executescript(pb_max_string)
    
    
    # pv to customers
    pc_max_string = """
                         drop table if exists max_pc;
                         create table max_pc as 
                         select site, reading_time, max(get_time) as max_ts
                         from pv_to_customer
                         group by site, reading_time;
                     """
    
    c = conn.cursor()
    c.executescript(pc_max_string)
    
    
    
    # battery to customers
    pc_max_string = """
                         drop table if exists max_bc;
                         create table max_bc as 
                         select site, reading_time, max(get_time) as max_ts
                         from battery_to_customer
                         group by site, reading_time;
                     """
    
    c = conn.cursor()
    c.executescript(pc_max_string)
    
    
    
    conn.commit()
    
    
    # =============================================================================
    # Re-create SSOT
    # =============================================================================
    
    ssot_str = """
    drop table if exists ssot;
    create table ssot as
    select  bs.site
           ,bs.reading_time
           ,bs.avg_bat
           ,ifnull(pb.pb,0) as pb
           ,ifnull(pc.pc,0) as pc
           ,ifnull(bc.bc,0) as bc
           ,ifnull(pc.pc,0) + ifnull(bc.bc,0) as tot_consumed
           ,ifnull(pc.pc,0) + ifnull(pb.pb,0) as tot_produced
           
    from
        max_base as mbase left join base as bs
            on mbase.max_ts = bs.get_time
            and mbase.reading_time = bs.reading_time
            and mbase.site = bs.site
            
        left join max_pb as mpb
            on mbase.reading_time = mpb.reading_time
            and mbase.site = mpb.site
        left join pv_to_battery as pb
            on mbase.reading_time = pb.reading_time
            and mbase.site = pb.site
            and mpb.max_ts = pb.get_time
        
        left join max_pc as mpc
            on mbase.reading_time = mpc.reading_time
            and mbase.site = mpc.site
        left join pv_to_customer as pc
            on mbase.reading_time = pc.reading_time
            and mbase.site = pc.site
            and mpc.max_ts = pc.get_time       
        
        left join max_bc as mbc
            on mbase.reading_time = mbc.reading_time
            and mbase.site = mbc.site
        left join battery_to_customer as bc
            on mbase.reading_time = bc.reading_time
            and mbase.site = bc.site
            and mbc.max_ts = bc.get_time              
    """
    
    c = conn.cursor()
    c.executescript(ssot_str)
    
    conn.commit()