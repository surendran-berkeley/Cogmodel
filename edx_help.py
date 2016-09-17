import json
import pandas as pd
import numpy as np
import re
import pickle
import time
from dateutil import parser


star_time= parser.parse("2014-02-24T00:30:00").replace(tzinfo=None) # official course start date
end_time= parser.parse("2014-03-31T09:30:00").replace(tzinfo=None) #official course end date

stat2014drops = ['problem_check_fail', 'edx.course.enrollment.upgrade.succeeded', 'list-staff','get-student-progress-page', 'save_problem_fail', 'showanswer','reset_problem_fail', 'rescore-student-submission','reset_problem','list-forum-admins','list-forum-mods','page_close',
 'edx.user.settings.changed','save_problem_success','reset-student-attempts','load_video','add-forum-admin','add-forum-mod', 'edx.forum.searched'] #List of event_type to drop from the study


event_set_1_list=['hide_transcript', 'speed_change_video', 'video_hide_cc_menu', 'seq_prev', 'seq_goto', 'show_transcript', 'load_video', 'seq_next', 'video_show_cc_menu', 'stop_video', 'pause_video', 'play_video']


event_set_2_list=['save_problem_success', 'reset_problem', 'problem_check_fail', 'save_problem_fail', 'showanswer'] #removed problem_check and have created a seperate function to handle the same

event_set_3_list=['problem_show']

event_set_4_list=['edx.course.enrollment.mode_changed', 'edx.course.enrollment.activated']

event_set_5_list= ['seek_video']
event_set_6_list= ['edx.course.enrollment.deactivated']




#######

enrollment_status={}
event_mapper={}
uname_unique={}
#slice_length={} #location of each element correspnds to the location uname in uname_unique and each element holds the value for number of time slices or number of elements

problem_check_state={}
#y_serialiser={}
#y_dict={}
problem_map={}
problem_mask={}
test_event={} #a test agent to track events mapped to be compared against a vector..

#########


#######

def event_set_1 (spl_data):
    load_data=spl_data["event"]
    eve= json.loads(load_data)
    event= eve["id"]
    return event


def event_set_2(spl_data):
    load_data=spl_data
    event= load_data['event']['problem_id']
    return event

def event_set_3(spl_data):
    load_data=spl_data["event"]
    eve= json.loads(load_data)
    event= eve["problem"]
    return event

def event_set_4(spl_data):
    load_data=spl_data
    event= load_data['event']['mode']
    return event

def event_set_5(spl_data):
    load_data=spl_data["event"]
    eve= json.loads(load_data)
    event= eve['id']
    return event


###########
event_map= json.load(open("event_map.json"))
event_map_concat= json.load(open("event_map_concat.json"))
load_country_code=json.load(open("country_id.json"))
load_action_code=json.load(open("actions.json"))
load_user_profie=json.load(open("user_profile.json"))
problem_id=json.load(open("problem_index.json"))
start_time=time.time()
country_counter={}
with open("ordered_BerkeleyX_Stat_2.1x_1T2014-events.log") as data:

    for i in data.readlines():
        load_data= json.loads(i)
        username= load_data["username"]


        try: #Check if username is present in event and if not handle key error by ignoring the event
            uname= re.findall("\d+", username)[0]
            if uname in event_mapper: #initate the first instance of user to the dictionary and check his entollment time with policy time
                pass
            else:
                event_mapper[uname]=[[]]
                test_event[uname]=[]
                #problem_check_state[uname]={}
                problem_map[uname]=[]
                problem_mask[uname]=[]
                student_start_time= parser.parse(load_data["time"]).replace(tzinfo=None)
                if star_time<student_start_time and end_time>student_start_time:
                    enrollment_status[uname]=1
                else:
                    enrollment_status[uname]=0
            try:
                country= load_data["augmented"]["country_code"]
                cid = load_country_code[country]
                if uname in country_counter:
                    pass
                else:
                    country_counter[uname]=country
            except KeyError: #If the key country_code is not present assigns null value to it
                cid = load_country_code["null"]
                if uname in country_counter:
                    pass
                else:
                    country_counter[uname]='NULL'

            try:
                a= load_user_profie[uname]
                user_details=a
                # if uname in load_user_profie:
                    #  user_details=load_user_profie[uname]
            except KeyError:
                user_details= [0,0,0]

            try:
                a= uname_unique[uname]
            except KeyError:
                uname_unique[uname]=0

            event=load_data["event_type"]

            if event[0] != "/" and event not in stat2014drops:
                aid= load_action_code[event]
            else:
                aid= load_action_code['null']

            if event in stat2014drops:
                uname_unique[uname]+=0
                continue

            elif event[0]== "/":
                new_row=[]
                uname_unique[uname]+=1
                eid= event_map[event]
                erid=event_map_concat[event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)
                test_event[uname]=eid

            elif event == "problem_check":
                y_array=[0]*len(problem_id)
                y_map=[0]*len(problem_id)
                new_row=[]
                location=len(event_mapper[uname][0])-1
                #tries to check the state as in whether it is a single unit problem or a series of sub problems so as to updat them accordingly
                if uname not in problem_check_state:
                    problem_check_state[uname]={}
                else:
                    pass
                for i in load_data["event"]["correct_map"]:
                    a = load_data["event"]["correct_map"]
                    correctness= a[i]["correctness"]
                    if correctness == "correct":
                        correct_val=1
                    else:
                        correct_val=0
                    try:
                        answers=load_data["event"]["answers"][i]
                        blank=0
                    except KeyError:
                        blank= 1
                    if i not in problem_check_state[uname] and blank==0:
                        problem_check_state[uname][i]=answers
                        c= i+"-"+ correctness
                        concat=c + event
                        eid=event_map[c]
                        erid=event_map_concat[concat]
                        uname_unique[uname]+=1
                        new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                        new_row.extend(user_details)
                        event_mapper[uname][0].append(new_row)
                        test_event[uname]=eid
                        y_array[(problem_id[i]-1)]=correct_val
                        y_map[(problem_id[i]-1)]=1
                    elif i not in problem_check_state[uname] and blank ==1:
                        pass

                    elif problem_check_state[uname][i]!= answers and blank==0:
                        c= i + "-" + correctness
                        concat=c+ event
                        problem_check_state[uname][i] = answers
                        eid=event_map[c]
                        erid=event_map_concat[concat]
                        uname_unique[uname]+=1
                        new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                        new_row.extend(user_details)
                        event_mapper[uname][0].append(new_row)
                        y_array[(problem_id[i]-1)]=correct_val
                        y_map[(problem_id[i]-1)]=1
                    else:
                        pass
                #print (y_array)
                #print (y_map)
                problem_map[uname].append((location, y_array))
                problem_mask[uname].append((location, y_map))

            elif event in event_set_1_list:
                new_row=[]
                uname_unique[uname]+=1
                event1=event_set_1(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)

            elif event in event_set_2_list:
                new_row=[]
                uname_unique[uname]+=1
                event1=event_set_2(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)

            elif event in event_set_3_list:
                new_row=[]
                uname_unique[uname]+=1
                event1=event_set_3(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)

            elif event in event_set_4_list:
                new_row=[]
                uname_unique[uname]+=1
                event1=event_set_4(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)

            elif event in event_set_5_list:
                new_row=[]
                uname_unique[uname]+=1
                event1=event_set_5(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)

            elif event in event_set_6_list:
                new_row=[]
                uname_unique[uname]+=1
                event1='ENROLLMENT_DEACTIVATED'
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid, enrollment_status[uname]]
                new_row.extend(user_details)
                event_mapper[uname][0].append(new_row)

        except IndexError: #Ignores the user events that don't have empty username value and therby throws Indexerror
            #print (load_data)
            pass
c=0
for i in uname_unique:
    if uname_unique[i]<=1209: #1209 is the upper bound of the timeslices eliminating the outliers (towards the upper side)
        pass
    else:
        if i in problem_check_state:
            del problem_check_state[i]
        else:
            pass

star_time=time.time()
g=0


time_slice_dict={}
for i in problem_check_state:
    time_slice_dict[i]=uname_unique[i]



#print (len(uname_filter))
print (len(problem_check_state))
row=len(problem_check_state)

final_country_problem_doers={}

for i in problem_check_state:
    final_country_problem_doers[i]=country_counter[i]

with open("country_profile.json", 'w') as cp:
    json.dump(final_country_problem_doers, cp)

with open ("event_slice_length.json", 'w') as et:
    json.dump(time_slice_dict, et)

input_tensor=np.zeros([row, 1209, 8], dtype="int16")
output_tensor=np.zeros([row, 1209, len(problem_id)], dtype="int16")
output_mask=np.zeros([row, 1209, len(problem_id)], dtype="int16")

row_counter=0
for i in problem_check_state:
    a= event_mapper[i]
    b=np.asarray(a)
    if len(b[0])==0:
        b=np.asarray([[[0,0,0,0,0,0,0,0]]])
    time_slice_length= len(a)
    input_tensor[row_counter, : len(b[0]), :8]= b
    for k in problem_map[i]:
        array_correct=np.asarray(k[1])
        output_tensor[row_counter, k[0], :len(problem_id)]=array_correct
    for l in problem_mask[i]:
        array_mask=np.asarray(l[1])
        output_mask[row_counter, l[0], :len(problem_id)]= array_mask
    row_counter+=1
end_time=time.time()


np.save("input_tensor", input_tensor)
np.save("output_tensor", output_tensor)
np.save("output_mask", output_mask)
