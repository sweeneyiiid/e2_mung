import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import datetime
from datetime import date, timedelta
from pprint import pprint

from support_functions import get_Hour_Minute, get_time_difference, get_wh_from_sockets

load_dotenv(find_dotenv())

# use DEV_MONGO_DATABASE_URI for dev and PROD_MONGO_DATABASE_URI for documentDB
# CONNECTION_STRING = os.getenv('DEV_MONGO_DATABASE_URI')
CONNECTION_STRING = os.getenv('PROD_MONGO_DATABASE_URI')
DB_NAME = "microgrid-ess"
# DB_NAME = "sandbox"

client = MongoClient(CONNECTION_STRING)
db = client[DB_NAME]

"""
WH transaction conversion and update
https://stackoverflow.com/questions/13554589/24-hour-time-conversion-to-12-hour-clock-problemsetquestion-on-python
STEPS
Get Time difference between sockets
Calculate Start Stop Values
Generate all  the start and stop from all sockets, sum them and multiply by the corresponding amp hours and what we need in wat hours which (amp x volt), volt is a constant
Append result to project
"""

coll_in_name = "historical_rekey"
collection = db[coll_in_name]

for r in collection.find(): # for each record in collection
    """
    STEPS
    Update or add  Add new field whSum into every whTransactions in the collection
    https://stackoverflow.com/questions/15666169/python-pymongo-how-to-insert-a-new-field-on-an-existing-document-in-mongo-fro
    """
    for index, wh in enumerate(r['whTransactions']): # for each record in whTransactions
        wh_from_sockets = round(get_wh_from_sockets(wh),2)
        # update nested wh transaction with sum of wh transactions 
        collection.update_one({"_id": r["_id"]}, {"$set": {"whTransactions."+ str(index) +".whSum": wh_from_sockets}}, upsert=True) #use upsert to update document if it doestn exist
# pprint(collection.find().limit(1))
print("processing done")