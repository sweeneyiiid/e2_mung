# Edison middleware

*NOTE: this code is derived in part from the open source bitbucket repository `edison_lite`*

 - SHS Paygo data
 - Victron minigrid management data
 - SMG (very idiosyncratic minigrid connection data)

### SHS Paygo 

Based on data from the Edison API loaded into MongoDB via POST requests to the Edison Endpoint.

 - contains two programs to go from raw data in MongoDB to a CSV file containing a snapshot of active connections as of a user-provided date
 - execution instructions in a README file within the `shs` folder

### Victron

 - Get request based on credentials shared by supported minigrid developers
 - hourly data (most granular available)
 
Program 1 `prog1_get_victron.py`:

 - adds "raw" results of GET request into MongoDB collection
 - manually update date parameters, can be MAX of 30 days apart
     - its ok to have duplicate/overlap, next program takes care of de-duping
 - relies on functions in the `support` folder
 
***NOTE: before next step only the FIRST time, you need to run initialization code.***

 - `./db_initialization/progX2_initialize_victron.py`: break out raw data from FIRST dump and establishes metric specific collections 

Program 2 `prog2_process_victron.py`:

 - de-dups new records, breaks into metrics, and adds to SSOT collection if they are AFTER current max time for that metrics
 - only processes one pull at a time (up to 30 days depending on parameters in program 1) 
 - so needs to be run repeatedly until it prints `nothing to update` to screen
 - ***user has to add credentials for mongodb, bad setup***
 
Then move to `prog3_victron_metrics.py`:

 - pulls data from SSOT collection, calculates metrics and dumps to CSV (entire series, indexed by day/hour)
 - ***user has to add credentials for mongodb, bad setup***

### SMG

 - Based on Microgrid customer subscription data posted to Edison endpoint
 - calculates amount Wh purchased by customer over a given period
     - energy avialability is pre-purchased, so may not actually be Wh consumed

 - The `smg` directory contains a more detailed README file

### SMG + Victron

In the case where we have victron data and customer data from a minigrid, we can combine this data to give a view of actual production and consumption vs. planned consumption (at the minigrid level, not the customer level since we do not have the data on actual consumption by customer).

This code was only executed in a pilot, and would need further testing to deploy for real.

More detail on the process is found in the `./smg/with_victron/` folder.


