# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 05:20:02 2022

https://www.sqlitetutorial.net/sqlite-python/creating-database/

@author: reeep
"""

import sqlite3

db_path = "C:/Users/reeep/OneDrive/Desktop/e2_cleanup/esp_db/esp_db_for_api.db"


conn = sqlite3.connect(db_path)

# create table

esp_table_str = """ CREATE TABLE IF NOT EXISTS esp (
                                        id integer PRIMARY KEY,
                                        name_company text,
                                        ext_id text,
                                        text_api_token text,
                                        text_notification_email text
                                    ); """



c = conn.cursor()
c.execute(esp_table_str)

#populate with test token

esp_insert = ''' INSERT INTO esp (name_company,ext_id,text_api_token,text_notification_email)
          VALUES('shs_company','asdf','testing_shs_token','stefan.zelazny@a2ei.org') '''

c.execute(esp_insert)

conn.commit()

conn.close()

# check

cur = conn.cursor()
cur.execute("SELECT * FROM esp")

rows = cur.fetchall()

print(rows)


