import json
import time
from datetime import datetime
import csv
import pickle
event_mappings ={}
event_mappings_actions_concat={}
country_json={None:0}
actions_json={None:0}
cleaned_timeinput_json=[]
user_profile= {}
json_dictionary={}
problem_index={}


### 1- uer id, 6- gender, 9- level of education, 9 - date of birth



stat2014drops = ['problem_check_fail',
             'edx.course.enrollment.upgrade.succeeded',
             'list-staff',
             'get-student-progress-page',
             'save_problem_fail',
             'showanswer',
             'reset_problem_fail',
             'rescore-student-submission',
             'reset_problem',
             'list-forum-admins',
             'list-forum-mods',
             'page_close',
             'edx.user.settings.changed',
             'save_problem_success',
             'reset-student-attempts',
             'load_video',
             'add-forum-admin',
             'add-forum-mod',
             'edx.forum.searched']
spl_event_types=['speed_change_video', 'page_close', 'problem_show', 'edx.user.settings.changed', 'edx.course.enrollment.deactivated', 'show_transcript', 'hide_transcript', 'seq_prev', 'edx.forum.searched', 'list-forum-mods', 'seq_next', 'reset_problem', 'get-student-progress-page', 'video_hide_cc_menu', 'seek_video', 'save_problem_success', 'list-staff', 'edx.course.enrollment.upgrade.succeeded', 'showanswer', 'reset-student-attempts', 'load_video', 'add-forum-mod', 'add-forum-admin', 'seq_goto', 'play_video', 'problem_check_fail', 'save_problem_fail', 'reset_problem_fail', 'rescore-student-submission', 'stop_video', 'edx.course.enrollment.mode_changed', 'video_show_cc_menu', 'problem_check', 'pause_video', 'list-forum-admins', 'edx.course.enrollment.activated']


event_set_1_list=['hide_transcript', 'speed_change_video', 'video_hide_cc_menu', 'seq_prev', 'seq_goto', 'show_transcript', 'load_video', 'seq_next', 'video_show_cc_menu', 'stop_video', 'pause_video', 'play_video']

event_set_2_list=['save_problem_success', 'reset_problem', 'problem_check_fail', 'save_problem_fail', 'showanswer'] #removed problem_check and have created a seperate function to handle the same

event_set_3_list=['problem_show']

event_set_4_list=['edx.course.enrollment.mode_changed', 'edx.course.enrollment.activated']

event_set_5_list= ['seek_video']
event_set_6_list= ['edx.course.enrollment.deactivated']


action_counter=1

for i in spl_event_types:
    if  i not in stat2014drops:
        actions_json[i]= action_counter
        action_counter+=1
    else:
        pass

# problem_check_state={}

counter=[]

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

def problem_check_event(spl_data, counter_1, counter_2):
    counter_1a= counter_1
    counter_2a=counter_2
    load_data=spl_data
    for i in load_data["event"]["correct_map"]:
        b= i
        assign_correctness_tags =  ['correct', 'incorrect']
        for val in assign_correctness_tags:
            c= i + "-" + val
            d= c+ load_data["event_type"]
            if c not in event_mappings and d not in event_mappings_actions_concat:
                event_mappings[c] = counter_1a
                event_mappings_actions_concat[d]=counter_2a
                counter_1a+=1
                counter_2a+=1
                counter.append(counter_2a)
            else:
                pass

    return(counter_1a, counter_2a)


def problem_counter_tracker(spl_data, problem_count):
    counter=problem_count
    load_data=spl_data
    for i in load_data["event"]["correct_map"]:
        if i not in problem_index:
            problem_index[i]=counter
            counter+=1
    return(counter)


def event_set_1 (spl_data):
    load_data=spl_data["event"]
    data=json.loads(load_data)
    event= data['id']
    return event


def event_set_2(spl_data):
    load_data=spl_data
    event= load_data['event']['problem_id']
    return event

def event_set_3(spl_data):
    load_data=spl_data["event"]
    data=json.loads(load_data)
    event= data["problem"]
    return event

def event_set_4(spl_data):
    load_data=spl_data
    event= load_data['event']['mode']
    return event

def event_set_5(spl_data):
    load_data=spl_data["event"]
    data=json.loads(load_data)
    event= data['id']
    return event


start_time= time.time()


with open("ordered_BerkeleyX_Stat_2.1x_1T2014-events.log") as data:
    counter_1=1
    counter_2 =1
    counter_country=1
    problem_count=1
    for line in data.readlines():
        load_data=json.loads(line)
        event_type=load_data["event_type"]
        time_elem= time_checker( load_data["time"])
        load_data["time"]=time_elem
        cleaned_timeinput_json.append(load_data)
        try:
            country=load_data["augmented"]["country_code"]
            if country not in country_json and country!= "UNKNOWN":
                country_json[country]=counter_country
                counter_country+=1
            else:
                pass
        except KeyError:
            pass

        if event_type in stat2014drops:
                continue
        elif event_type[0]== "/" and (event_type  not in event_mappings and event_type not  in event_mappings_actions_concat):
            a= event_type
            event_mappings[a]= counter_1
            event_mappings_actions_concat[a]=counter_2
            counter_1+=1
            counter_2+=1
            counter.append(counter_2)


        elif event_type == "problem_check":
            a,b=problem_check_event(load_data, counter_1, counter_2)
            c= problem_counter_tracker(load_data, problem_count)
            problem_count=c
            counter_1=a
            counter_2=b

        elif event_type in event_set_1_list:
            a = event_set_1(load_data)
            b= a+'-'+event_type
            if a not in event_mappings:
                event_mappings[a] =counter_1
                counter_1+=1
            else:
                pass
            if b not in event_mappings_actions_concat:
                event_mappings_actions_concat[b]=counter_2
                counter_2+=1
                counter.append(counter_2)
            else:
                pass


        elif event_type in event_set_2_list:
            a = event_set_2 (load_data)
            b= a+'-'+event_type
            if a not in event_mappings:
                event_mappings[a] =counter_1
                counter_1+=1
            else:
                pass
            if b not in event_mappings_actions_concat:
                event_mappings_actions_concat[b]=counter_2
                counter_2+=1
                counter.append(counter_2)
            else:
                pass


        elif event_type in event_set_3_list:
            a = event_set_3 (load_data)
            b= a+'-'+event_type
            if a not in event_mappings:
                event_mappings[a] =counter_1
                counter_1+=1
            else:
                pass
            if b not in event_mappings_actions_concat:
                event_mappings_actions_concat[b]=counter_2
                counter_2+=1
                counter.append(counter_2)
            else:
                pass


        elif event_type in event_set_4_list:
            a = event_set_4 (load_data)
            b= a+'-'+event_type
            if a not in event_mappings:
                event_mappings[a] =counter_1
                counter_1+=1
            else:
                pass
            if b not in event_mappings_actions_concat:
                event_mappings_actions_concat[b]=counter_2
                counter_2+=1
                counter.append(counter_2)
            else:
                pass


        elif event_type in event_set_5_list:
            a = event_set_5 (load_data)
            b= a+'-'+event_type
            if a not in event_mappings:
                event_mappings[a] =counter_1
                counter_1+=1
            else:
                pass
            if b not in event_mappings_actions_concat:
                event_mappings_actions_concat[b]=counter_2
                counter_2+=1
                counter.append(counter_2)
            else:
                pass

        elif event_type in event_set_6_list:
            a = 'ENROLLMENT_DEACTIVATED'
            b= a+'-'+event_type
            if a not in event_mappings:
                event_mappings[a] =counter_1
                counter_1+=1
            else:
                pass
            if b not in event_mappings_actions_concat:
                event_mappings_actions_concat[b]=counter_2
                counter_2+=1
                counter.append(counter_2)
            else:
                pass

###### User Profile generator and parser
age={"NULL":0}
education={"NULL":0}
gender={'NULL':0,'m':1,'f':2}
age_count=1
education_count=1
profile=open("BerkeleyX-Stat_2.1x-1T2014-auth_userprofile-prod-analytics.sql")
profile_csv= csv.reader(profile, delimiter="\t")
for i in profile_csv:
    if i[1] not in user_profile:
        age_now=i[9]
        if age_now != "NULL" and age_now not in age:
            age[age_now]=age_count
            age_count+=1
        else:
            pass
        if i[10] != 'NULL' and i[10] not in education:
            education[i[10]]=education_count
            education_count+=1
        else:
            pass
        if i[7] != 'NULL' and i[7]!='m' and i[7]!='f':
            i[7]="NULL"
        else:
            pass
        user_profile[i[1]]=[age[age_now], education[i[10]], gender[i[7]]]



"""sorted_input_json = sorted(cleaned_timeinput_json, key=lambda k: k["time"], reverse=False)
k = open("test.log", 'w')
for i in sorted_input_json:
    print (i, file= k)"""
### dictionary of user profile:

end_time=time.time()
time_taken= (end_time - start_time)
with open("event_map.json", "w") as fp:
    json.dump(event_mappings, fp)
with open("event_map_concat.json",'w') as  kp:
    json.dump(event_mappings_actions_concat, kp)

with open("country_id.json", "w") as pp:
    json.dump(country_json, pp)

with open("actions.json", "w") as lp:
    json.dump(actions_json, lp)

'''with open("time_sorted_input_edx", 'wb') as ts:
    pickle.dump(sorted_input_json, ts)'''

with open("user_profile.json", "w") as up:
    json.dump(user_profile, up)

with open("problem_index.json", 'w') as pi:
    json.dump(problem_index, pi)


print (time_taken)
print (len(event_mappings))
print (len(event_mappings_actions_concat))
print(len(counter))
print (len(problem_index))
