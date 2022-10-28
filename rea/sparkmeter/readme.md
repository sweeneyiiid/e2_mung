# REA Kasanjiku apark meters


# Staging up

bright gave access to thundercloud test platform

http://sparkapp-staging.spk.io:5010/login?next=%2F

rea had already set up test api user


followed documentation below to get user api key:

https://api.sparkmeter.io/

http://sparkapp-staging.spk.io:5010/api/v0/



### linux

```
curl --location --request GET 'http://sparkapp-staging.spk.io:5010/api/v0/system-info' --header 'Content-Type: application/json' --header 'Authentication-Token: .eJwNyMERgDAIBMBeeMsMcEnEWhwfSKD_EnSfexMu6_JIFoTyKDcOXINbNzK7MTfoIK-yM_5bU-G7TasFqqK5XjHQ8wHv4xOH.YymoMw.Ti6F5CjwSrjPpjS3Us-FOfXnRwQ'
```


### windows

```
curl --location --request GET "http://sparkapp-staging.spk.io:5010/api/v0/system-info" --header "Content-Type: application/json" --header "Authentication-Token: .eJwNyMERgDAIBMBeeMsMcEnEWhwfSKD_EnSfexMu6_JIFoTyKDcOXINbNzK7MTfoIK-yM_5bU-G7TasFqqK5XjHQ8wHv4xOH.YymoMw.Ti6F5CjwSrjPpjS3Us-FOfXnRwQ"
```

Testing platform worked, now time to move onto actual platform.

Now have access to actual credentials (and production endpoint), will test those really quick using same command as above in windows.

***OK, real key works!***

Ok, so basic access works, now try to get some more interesting stuff.


# Run through Sparkmeter GET requests

For this I am switching to python `scratch_check.py`.

 - so the basic pulls are pretty straightforward
 - within a customer record, there can be multiple meters and grounds, but not sure how common that is
 - but since the meter record is what we want anyway, probably makes sense to break those out separately
 
so remaining stuff:

 - get a solid meter dataframe (possibly via for loop, although hopefully there is a way to vectorize)
     - yeah, can confirm only one meter per customer in current dataset
 - start mapping out which fields we can get, what they mean
 - start putting together questions for sparkmeter folks
 
## Interesting fields

 - within customers > meters (removed some fields that didn't seem as interesting)
 
```
sites_json['customers'][0]['meters'][0]
Out[46]: 
{'active': True,
 'address': 'A-3, Mwinilunga, North Western Province, Zambia',
 'coords': '',
 'country': 'Zambia',
 'current_daily_energy': None,
 'current_tariff_name': 'Medium Consumption',
 'is_running_plan': True,
 'last_config_datetime': '2022-08-31T07:45:22.749814',
 'last_cycle_start': '2022-10-03T11:59:59',
 'last_energy': 1404.76590625,
 'last_energy_datetime': '2022-10-27T11:00:00',
 'last_meter_state_code': 1,
 'last_plan_expiration_date': '2022-10-27T19:00:00',
 'last_plan_payment_date': '2022-10-26T19:00:00',
 'operating_mode': 2,
 'plan_balance': 7.90884062499923,
 'postalcode': '',
 'serial': 'SM60R-07-0002334E',
 'total_cycle_energy': 160.068281249999}
```

Based on random pulls, it appears 

## Initial questions for REA and SparkMeter

### REA

 - who works with this data now, and how does the tariff system work?
     - I think pseudo tariff at this point
 - does anyone actually monitor the energy use via the meters, or is that done through the SCADA at the main plant?
 
### SparkMeter

 - any way to pull historical data through the API?
 - is `last_energy` within the customer -> meter API a snapshot measured in Watts?
 - is `total_cycle_energy` in the same structure the cumulative kWh since `last_cycle_start`?
    - and how long/standardized is a cycle? (maybe that's a question for REA as well)
 - what happens if a meter is out of contact for some reason, does `total_cycle_energy` still accumulate?

