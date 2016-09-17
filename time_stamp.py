import json
import time
from datetime import datetime
import csv
import pickle



def time_checker(input_time):
    time_element=input_time
    if '+' in time_element:
        if '.' in time_element:
            date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        else:
            date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
    elif '.' in time_element:
        date_object = datetime.strptime(time_element, '%Y-%m-%dT%H:%M:%S.%f')
    else:
        date_object = datetime.strptime(time_element, '%Y-%m-%dT%H:%M:%S')

    json_serial= date_object.isoformat()
    return(json_serial)

time_stamp=[]


with open("BerkeleyX_Stat_2.1x_1T2014-events.log") as data:

    for line in data.readlines():
        load_data=json.loads(line)
        time_elem= time_checker( load_data["time"])
        time_stamp.append(time_elem)


print (time_stamp)
