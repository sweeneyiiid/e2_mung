

## STEP 1: Pull data from MongoDB and Process
 
The raw shs data is stored in a collection based on the SHS company name and contains information about the customer and system purchased (which does not change) as well as payment information (which changes).
 
So program 1 has two steps.  

 - The first step collects SHS (Solar Home System) and customer information and de-duplicates it by selecting the information from the last record received.
 - The second step collects payment information and de-duplicates it **ONLY** at the payment record level, to have a record of each payment associated with each SHS
 
The output of the program is two CSV files in a SQL table format.  Note that there is no "as-of" component in progam 1 (that will be handled in program 2).  This program processes all the data available to it.

 - Input: raw MongoDB collection
 
```
python3 prog1_normalize_shs.py
```

 - Output: `./data/shs_dump.csv` and `./data/pmt_dump.csv`
 
## STEP 2: Take snapshot of status as-of a given date

Program 2 summarizes the payment information as of a given date (provided by the user in the program code) and merges it back to the customer data for downstream analysis.

Currently the programme defines the "as-of" date as day after the end of the program (2022-01-31).  If you want to change that, change this line in the code:

```
as_of_str = "2022-02-01"
```

Note that this also automatically changes the name of the output file.

 - Input: `./data/shs_dump.csv` and `./data/pmt_dump.csv`
 
```
python3 prog2_get_shs_normalized.py
```

 - Output: `./data/shs_data_asof_YYYY-MM-DD.csv`


