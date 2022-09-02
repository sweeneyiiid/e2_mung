from datetime import datetime

"""
function to get hour and minute from military time format
https://stackoverflow.com/questions/13554589/24-hour-time-conversion-to-12-hour-clock-problemsetquestion-on-python
"""
def get_Hour_Minute(input):
    return datetime.strptime(input, '%H%M').strftime('%H:%M:%S').lower()
    # return datetime.strptime(input, '%H%M:')

"""
function to get time difference between two hour minutes
https://stackoverflow.com/questions/3096953/how-to-calculate-the-time-interval-between-two-time-strings
changed to using total seconds instead: https://docs.python.org/3/library/datetime.html#datetime.timedelta.total_seconds
"""
def get_time_difference(start, end):
    FMT = '%H:%M:%S'
    s1 = get_Hour_Minute(start)
    s2 = get_Hour_Minute(end)
    dt = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
    #dt_h_m = datetime.strptime(str(dt), FMT).strftime('%H.%M')
    #return float(dt_h_m)

    #seconds to hours (as float)
    return dt.total_seconds()/3600


"""
function to get wh from start and end sockets
all the start and stop from all sockets, sum them and multiply by the corresponding amp hours and what we need in wat hours which is (amp x volt), volt is a constant @ 2.3.
STEPS
Select each socket by looping through it from 1 < 5
Select start stop and loop through it from 0 < 4check time difference between start and stop
TODO: fix 1 hour return for 00 time
Get Cent amp limit with the socket loop
"""
def get_wh_from_sockets(x):
    num_days_purch = x['nbrDaysPurchased']
    watt_cum = 0 # cummilative of socket  watts
    for socket in range(1,6): # looping through sosckets from 1 < 5
        # centaAmp = x["nbrCentaAmpLimit"+ str(socket)]
        centaAmp = x.get("nbrCentaAmpLimit"+ str(socket), 0)
        sumSockets = 0 # increament value of sockets

        for start_stop in range(5): # looping through sosckets start stop from 0 < 4
            
            # TODO: ignore sockets not found https://www.jquery-az.com/python-keyerror-handle-3-examples/#:~:text=Second%20way%20%E2%80%93%20Using%20the%20get,default%2C%20it%20defaults%20to%20None.
            # start = x["socket"+ str(socket)+"Start"+ str(start_stop)] #get each start from Start1 - Start5
            # start = x.get("socket"+ str(socket)+"Start"+ str(start_stop)) or '0000'#get each start from Start1 - Start5
            start = x.get("socket"+ str(socket)+"Start"+ str(start_stop), "0000") #get each start from Start1 - Start5
            # stop = x["socket"+ str(socket)+"Stop"+ str(start_stop)]  #get each stop from Stop1 - Stop5
            # stop = x.get("socket"+ str(socket)+"Stop"+ str(start_stop)) or '0000'  #get each stop from Stop1 - Stop5
            stop = x.get("socket"+ str(socket)+"Stop"+ str(start_stop), "0000")  #get each stop from Stop1 - Stop5
            difference = get_time_difference(start, stop)
            sumSockets += difference
            
        watt_from_sockets = (int(centaAmp) * sumSockets) * 2.3 #total watts from sockets
        watt_cum += watt_from_sockets

    wh_final = watt_cum * int(num_days_purch)
    return wh_final
