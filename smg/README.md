# SMG Manual run


***NOTES:*** 

 - Dependent on a config (`.env`) file
     - needs to be present somewhere in the parent directory
     - contains the connection string used by python to access MongoDB
     - do **NOT** include in the git repo though, as it contains the password



### STEP 1: Remove duplicates in data

SMG sends in raw data for every customer electricity purchase it makes.  It is possible that SMG will send the same record twice.  To avoid double counting, the first script only keeps the most recently sent record of each transation, based on the time the record was processed into our system.  For deprecated historical reasons, it also takes the raw microgrid-ess data and replaces the transaction key with the customer key (this used to be so that we could track multiple transactions across a customer, but we now do that differently).

Since there is so little SMG data, the code does not attempt to identify new records only, it simply re-processes all SMG data and dumps the data into a new location so that the raw SMG data is preserved.

 - input collection: `Standard Microgrid` (raw data)

```
python3 prog1_de_duplication.py
```

 - output collection: `de_duplication`

### STEP 2: calculate Wh by transaction

This script calculates the Wh purchased in each customer transaction using the times power is available, the amperage purchased, and the voltage (which is assumed constant at 230v).

The script accesses the de-duplicated data and adds a new field for the Wh purchased in each transaction and dumps it into a new collection.

 - input collection: `de_duplication`

```
python3 prog2_wh_accumulation_vectorized.py
```

 - output collection: `wh_accumulation`

### STEP 3: flatten Wh transactions into tabular structure

This script accesses the Wh accumulation data, and pulls key fields from out of the nested structure and dumps them in a new collection without any nested data so that the structure is more like a tradional table.  This is the last step before the data is dumped into python for processing.

 - input collection: `wh_accumulation`

```
python3 prog3_wh_to_table_historical.py
```

 - output collection: `wh_flatten`

### STEP 4: get data by day for each customer

This script pulls the data from mongoDB into python and imposes all of the transaction data onto a calendar, then sums the data by the dates specified to show how much total energy access (in Wh) each customer had available during a given (typically 90 day) period.

The output is a CSV file which is analyzed in excel to create the reporting metrics.

***NOTES:***

 - this is the only script where parameters (the to and from date) must be set before running
 - per_start should be the last day of the previous quarter (or measureing period) and per_end should be the fist day of the next quarter (or measuring period)

First update the dates (typically to the 90 day period ending the day of the run or of the 90 days ending on the 1st day of the month) as well as optionally the output file name:

```
#IMPORTANT: the three variables below are the ones to be changed
out_path_exhibit = './smg_monitoring_20220519.csv'
per_start = pd.to_datetime('2022-02-17')
per_end = pd.to_datetime('2022-05-20')
```

Next execute the script:

 - input collection: `wh_flatten`

```
python3 prog4_smg_ssot.py
```

 - output: CSV file in directory where script was executed, named per above

The script should output a CSV file in the directory from which it was executed, transfer this to local (Dan uses WinSCP, but any STFP client will do)










