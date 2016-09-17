import json
import pandas as pd
import numpy as np
import re
import pickle
import ast


pl_event_types=['speed_change_video', 'page_close', 'problem_show', 'edx.user.settings.changed', 'edx.course.enrollment.deactivated', 'show_transcript', 'hide_transcript', 'seq_prev', 'edx.forum.searched', 'list-forum-mods', 'seq_next', 'reset_problem', 'get-student-progress-page', 'video_hide_cc_menu', 'seek_video', 'save_problem_success', 'list-staff', 'edx.course.enrollment.upgrade.succeeded', 'showanswer', 'reset-student-attempts', 'load_video', 'add-forum-mod', 'add-forum-admin', 'seq_goto', 'play_video', 'problem_check_fail', 'save_problem_fail', 'reset_problem_fail', 'rescore-student-submission', 'stop_video', 'edx.course.enrollment.mode_changed', 'video_show_cc_menu', 'problem_check', 'pause_video', 'list-forum-admins', 'edx.course.enrollment.activated']

event_set_1_list=['hide_transcript', 'speed_change_video', 'video_hide_cc_menu', 'seq_prev', 'seq_goto', 'show_transcript', 'load_video', 'seq_next', 'video_show_cc_menu', 'stop_video', 'pause_video', 'play_video']


event_set_2_list=['save_problem_success', 'reset_problem', 'problem_check_fail', 'save_problem_fail', 'showanswer'] #removed problem_check and have created a seperate function to handle the same

event_set_3_list=['problem_show']

event_set_4_list=['edx.course.enrollment.mode_changed', 'edx.course.enrollment.activated']

event_set_5_list= ['seek_video']
event_set_6_list= ['edx.course.enrollment.deactivated']

ignore_list= ["edx.course.enrollment.upgrade.succeeded", "list-staff", "get-student-progress-page","reset_problem_fail", "rescore-student-submission", "source", "edx.forum.searched", "list-forum-admins","list-forum-mods", "edx.user.settings.changed", "reset-student-attempts","add-forum-admin", "add-forum-mod"]




#######


event_mapper={}
uname_unique=[]
slice_length=[] #location of each element correspnds to the location uname in uname_unique and each element holds the value for number of time slices or number of elements

problem_check_state={}
#y_serialiser={}
#y_dict={}

#####
"""def problem_check_event(spl_data):
    load_data=spl_data
    uname=load_data["event_type"]
    if uname not in problem_check_state:
        problem_check_state[uname]={}
    else:
        pass
    for i in load_data["event"]["correct_map"]:
        correctness= i["correctness"]
        answers=load_data["event"]["answers"]["i"]
        if i not in problem_check_state[uname]:
            problem_check_state[uname][i]=answers
            c= i+"-"+ correctness
            return (c)
        else:
            if problem_check_state[uname][i]!= answers:
                c= i + "-" + correctness
                problem_check_state[uname][i] = answers
                return c
            else:
                return (None)"""




def event_set_1 (spl_data):
    load_data=spl_data["event"]
    eve= ast.literal_eval(load_data)
    event= eve["id"]
    return event


def event_set_2(spl_data):
    load_data=spl_data
    event= load_data['event']['problem_id']
    return event

def event_set_3(spl_data):
    load_data=spl_data["event"]
    eve= ast.literal_eval(load_data)
    event= eve["problem"]
    return event

def event_set_4(spl_data):
    load_data=spl_data
    if isinstance(load_data["event"], dict):
        event= load_data['event']['mode']
        return event
    else:
        #print (load_data)
        #print (type(load_data["event"]))
        return None

def event_set_5(spl_data):
    load_data=spl_data["event"]
    try:
        eve= ast.literal_eval(load_data)
        event= eve['type']
        return event
    except ValueError:
        print (load_data)
        return ("onCaptionSeek")
        print ("a")


###########

with open("test.log") as data:
    event_map= json.load(open("event_map.json"))
    event_map_concat= json.load(open("event_map_concat.json"))
    load_country_code=json.load(open("country_id.json"))
    load_action_code=json.load(open("actions.json"))
    load_user_profie=json.load(open("user_profile.json"))
    for i in data.readlines():
        load_data= ast.literal_eval(i)
        username= load_data["username"]
        try:
            uname= re.findall("\d+", username)[0]
            event_mapper[uname]=[]
            try:
                country= load_data["augmented"]["country_code"]
                cid = load_country_code[country]
            except KeyError:
                cid = load_country_code["null"]

            if uname in load_user_profie:
                user_details=load_user_profie[uname]
            else:
                user_details= None
            if uname in uname_unique:
                pass
            else:
                uname_unique.append(uname)
                slice_length.append(0)

            event=load_data["event_type"]

            if event[0] != "/" and event not in ignore_list:
                aid= load_action_code[event]
            else:
                aid= load_action_code['null']

            if event in ignore_list:
                slice_length[uname_unique.index(uname)]+=0

            elif event[0]== "/":
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                eid= event_map[event]
                erid=event_map_concat[event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

            elif event == "problem_check":
                new_row=[]
                if uname not in problem_check_state:
                    problem_check_state[uname]={}
                else:
                    pass
                for i in load_data["event"]["correct_map"]:
                    a= load_data["event"]["correct_map"]
                    correctness= a[i]["correctness"]
                    try:
                        answers=load_data["event"]["answers"][i]
                    except KeyError:
                        answers= None
                    if i not in problem_check_state[uname]:
                        problem_check_state[uname][i]=answers
                        c= i+"-"+ correctness
                        concat=c + event
                        eid=event_map[c]
                        erid=event_map_concat[concat]
                        slice_length[uname_unique.index(uname)]+=1
                        new_row=[eid, aid, erid, cid]
                        new_row.append(user_details)
                        event_mapper[uname].append(new_row)
                    else:
                        if problem_check_state[uname][i]!= answers:
                            c= i + "-" + correctness
                            concat=c+ event
                            problem_check_state[uname][i] = answers
                            eid=event_map[c]
                            erid=event_map_concat[concat]
                            slice_length[uname_unique.index(uname)]+=1
                            new_row=[eid, aid, erid, cid]
                            new_row.append(user_details)
                            event_mapper[uname].append(new_row)
                        else:
                            pass

            elif event in event_set_1_list:
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                event1=event_set_1(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

            elif event in event_set_2_list:
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                event1=event_set_2(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

            elif event in event_set_3_list:
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                event1=event_set_3(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

            elif event in event_set_4_list:
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                event1=event_set_4(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

            elif event in event_set_5_list:
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                event1=event_set_5(load_data)
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

            elif event in event_set_6_list:
                new_row=[]
                slice_length[uname_unique.index(uname)]+=1
                event1='ENROLLMENT_DEACTIVATED'
                eid= event_map[event1]
                concat_event=event1+"-"+event
                erid=event_map_concat[concat_event]
                new_row=[eid, aid, erid, cid]
                new_row.append(user_details)
                event_mapper[uname].append(new_row)

        except IndexError:
            #print (load_data)
            pass

input_tensor= np.zeros([len(uname_unique), max(slice_length), 7], dtype="int8")
row_counter=0
for i in uname_unique:
    a= event_mapper[i]
    time_slice_length= len(a)
    input_tensor[row_counter, : (len(time_slice_length)-1)]= a
    row_counter+=1

np.save("input_tensor", input_tensor)
