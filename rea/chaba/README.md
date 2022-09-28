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


## Move from SQLite to MySQL\

I have the program set up with SQLite, but I dont like it, because I am worried it actually won't be a smooth transition to Postgresql.

However, I don't really know of a quick and easy way to set up a instance, but it seems like if I use SQLalchemy even with MySQL, hopefully SQLalchemy will know what to do [when we switch to Postgresql](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html).

So I set up a free instance of [MySQL online](https://www.freemysqlhosting.net/):

```
Server: sql11.freemysqlhosting.net
Name: sql11522555
Username: sql11522555
Password: 
Port number: 3306
```

Now the goal will be to redo the steps below using SQLalchemy.  Once that's done, still need to refactor the code.

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
 
