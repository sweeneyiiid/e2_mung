

import time
from datetime import datetime, date, time, timedelta
#from apscheduler.schedulers.background import BackgroundScheduler
import datetime as dt

# """
# Periodic data saving from victron
# """
# from app.jobs.victron_daily import run_vic_daily
# from app.jobs import victron_daily

# da = "2021-10-29 00:00:00"
# d2 = "2021-10-30 00:00:00"

# # dt = datetime.combine("2022-02-01", time(0, 0, 0))
# dt = datetime.strptime(da, '%Y-%m-%d %H:%M:%S')
# dt2 = datetime.strptime(d2, '%Y-%m-%d %H:%M:%S')

# print(dt)

# run_vic_daily(date_end=dt2, date_start=dt)

import app.jobs.victron_daily as vc

#dates = ["2021-10-01", "2021-11-01", "2021-12-01", "2022-01-01", "2022-02-01", "2022-03-01", "2022-04-01"]
dates = ["2022-04-26", "2022-05-01", "2022-06-01"]


for i in range(len(dates)-1):
    
    x = dt.datetime.strptime(dates[i], "%Y-%m-%d")
    y = dt.datetime.strptime(dates[i+1], "%Y-%m-%d")

    vc.run_vic_daily(date_end=y, date_start=x)
    print("\nprocessed month: "+str(x)+ "\n")

# """
# Data schedular 
# cron jobs = victron every day
# """
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(run_vic_daily, trigger='cron', year='*', month='*', day=1)



# # test token service

# from app.services.token_service import TokenService
# token_service = TokenService()
# token = token_service.get_token()
# # print(token)


# # # get victron data with class
# from app.services.victron_service import VictronService

# # keep track on start and end
# # TODO: timestamp pulled, 

# start = 1638964800
# end = 1639051200

# victron = VictronService(token,start, end)
# # victron_data = victron.get_data()
# # print(victron_data)

# # save to mongo service
# save_to_mongo = victron.output()
# print(save_to_mongo)


