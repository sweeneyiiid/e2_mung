# Victron for Chaba minigrid

similar metrics to old Kampekete setup.

HOWEVER, we are moving away from MongoDB, so a lot of this code will relate to that transition.

# Pull in data

 - same as kampekete (although unwound some classes into notebook code)
 - read into pandas instead of MongoDB
 
# Data storage

 - not doing anything with raw data right now, IRL should dump into a JSON in some data lake or something like that.
 
## SQLite

 - mimic Postgresql where data will be IRL
 - steps below are temporary, may or may not be what IRL setup looks like
 
### Transactional table

 - record for every pull, even if the same metric for the same hour is pulled multiple times
 - include a field for time of pull
 
### Max date table

 - run a query to find the max pulled date for each combination of metric and reading datetime
 - use to figure out what to pull for de-duped table
 
### de-duped table

 - join transaction table in max date table to get actual readings


### all metrics table

 - do some kind of pivot to get all metrics as columns by hour
 
