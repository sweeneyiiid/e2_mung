# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 09:35:17 2022

@author: DanielSweeney
"""
import pymongo

DEV_MONGO_DATABASE_URI = "mongodb+srv://<user>:<password>@cluster0.ok5iq.mongodb.net/microgrid?retryWrites=true&w=majority"



client = pymongo.MongoClient(DEV_MONGO_DATABASE_URI)

#database name
db_name = "victron"
db = client[db_name]

#input collection name
pipe_in_coll = "initial_dump"


# based on the first record we got right
# time_stamp:1648555450.612752
first_rec_ts = 1648555448.3631759


#output collection
pipe_out_coll = "ssot"


#metrics to process
metrics = ['bs', 'Bc', 'Pc', 'Pb']

#for join: battery storage should be the base metric, since will have status for all hours
base_metric = 'bs'
join_metrics = metrics.copy()
join_metrics.remove(base_metric)

# =============================================================================
# Step 1: Pull earliest single record of raw data and process metrics
# =============================================================================

pipelines = []

#same pipeline for each metric
for mx in metrics:
    pipelines.append([
                # https://www.mongodb.com/docs/v5.0/reference/operator/aggregation/match/
                { 
                    '$match' : { 'time_stamp' : first_rec_ts } 
                },
                # https://docs.mongodb.com/manual/reference/operator/aggregation/first/
                {
                    '$sort':  { 'success': 1, 'time_stamp': 1 }
                },
                {
                    '$group':  {
                        '_id': '$success',
                        'first_pull': {'$first':'$time_stamp'},
                        mx: { '$first':'$records.' + mx}
                        }
                },
                #https://docs.mongodb.com/manual/reference/operator/aggregation/unwind/
                {
                    '$unwind':'$' + mx
                },
                #https://bitbucket.org/reeep/smg_integration/src/master/mongodb/ad_hoc/wh_to_table_historical.py
                {
                    '$set': {
                        'unix_hour':{'$arrayElemAt':['$' + mx,0]},
                        mx + '_reading':{'$arrayElemAt':['$' + mx,1]}
                        }
                },
                {
                    '$project':{
                            '_id':'$unix_hour',
                            'unix_hour':1,
                            mx + '_reading':1,
                            'ts_pulled':'$first_pull'
                            } 
                },
                {
                    '$out': 'metric_' + mx
                }
            ])

    
#execute pipelines
for pipe in pipelines:
    check = list(db[pipe_in_coll].aggregate(pipe))
    print(str(check))



# =============================================================================
# Step 2: combine individual metric collections
# =============================================================================




join_pipeline = [
    {
        '$project':{
                'unix_hour':1,
                base_metric + '_reading':1,
                base_metric+'_pulled':'$ts_pulled'
                }
    }
        
]

for mx in join_metrics:
    join_pipeline = join_pipeline + [
                    {
                        '$lookup':{
                                'from': 'metric_' + mx,
                                'localField': '_id',
                                'foreignField': '_id',
                                'as': 'rec_from_' + mx
                       }
                    },
                    {
                        '$set': {
                            'temp':{'$arrayElemAt':['$rec_from_'+ mx,0]}
                            }
                
                    },
                    {
                        '$set': {
                            mx+'_reading':'$temp.'+mx+'_reading',
                            mx+'_pulled':'$temp.ts_pulled'
                            }
                
                    },
                    {
                        '$unset':['temp','rec_from_'+ mx]
                    }]



join_pipeline.append({'$out':pipe_out_coll})
    
    
check_data = list(db['metric_' + base_metric].aggregate(join_pipeline))

check_data

