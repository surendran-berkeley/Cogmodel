import json
import time
import csv

score_kepper={}
event_mappings ={}

spl_event_types=['speed_change_video', 'page_close', 'problem_show', 'edx.user.settings.changed', 'edx.course.enrollment.deactivated', 'show_transcript', 'hide_transcript', 'seq_prev', 'edx.forum.searched', 'list-forum-mods', 'seq_next', 'reset_problem', 'get-student-progress-page', 'video_hide_cc_menu', 'seek_video', 'save_problem_success', 'list-staff', 'edx.course.enrollment.upgrade.succeeded', 'showanswer', 'reset-student-attempts', 'load_video', 'add-forum-mod', 'add-forum-admin', 'seq_goto', 'play_video', 'problem_check_fail', 'save_problem_fail', 'reset_problem_fail', 'rescore-student-submission', 'stop_video', 'edx.course.enrollment.mode_changed', 'video_show_cc_menu', 'problem_check', 'pause_video', 'list-forum-admins', 'edx.course.enrollment.activated']

event_set_1_list=['hide_transcript', 'speed_change_video', 'video_hide_cc_menu', 'seq_prev', 'seq_goto', 'show_transcript', 'load_video', 'seq_next', 'video_show_cc_menu', 'stop_video', 'pause_video', 'play_video']


event_set_2_list=['save_problem_success', 'reset_problem', 'problem_check_fail', 'save_problem_fail', 'showanswer'] #removed problem_check and have created a seperate function to handle the same

event_set_3_list=['problem_show']

event_set_4_list=['edx.course.enrollment.mode_changed', 'edx.course.enrollment.activated']

event_set_5_list= ['seek_video']
event_set_6_list= ['edx.course.enrollment.deactivated']

ignore_list= ["edx.course.enrollment.upgrade.succeeded", "list-staff", "get-student-progress-page","reset_problem_fail", "rescore-student-submission", "source", "edx.forum.searched", "list-forum-admins","list-forum-mods", "edx.user.settings.changed", "reset-student-attempts","add-forum-admin", "add-forum-mod"]

problem_check_state={}



def problem_check_event(spl_data, counter):
    load_data=spl_data
    uname=load_data["usernme"]
    if uname not in problem_check_state:
        problem_check_state[uname]={}
    else:
        pass
    for i in load_data["event"]["correct_map"]:
        correctness= i["correctness"]
        answers=load_data["event"]["answers"]["i"]
        if i not in problem_check_state[uname]:
            problem_check_state[uname][i]=answers
        else:
            if problem_check_state[uname][i]!= answers:
                c= i + "-" + correctness
                mapper={}
                mapper["event_id"]= event_mapper[c]
                mapper ["name"]= spl_data["username"]
                mapper ["time"]= spl_data["time"]
                mapper["action"] = spl_data["event_type"]
                mapper["country"]= spl_data["augmented"]["country_code"]
                mapper["event_source"]=spl_data["event_source"]
                mapper["session"]= spl_data["session"]
                final_list.append(mapper)
            else:
                pass



def event_set_1 (spl_data):
    load_data=spl_data["event"]
    data=json.loads(load_data)
    event= data['id']
    mapper={}
    mapper["event_id"]= event_mapper[event]
    mapper ["name"]= spl_data["username"]
    mapper ["time"]= spl_data["time"]
    mapper["action"] = spl_data["event_type"]
    mapper["country"]= spl_data["augmented"]["country_code"]
    mapper["event_source"]=spl_data["event_source"]
    mapper["session"]= spl_data["session"]
    final_list.append(mapper)

def event_set_2(spl_data):
    load_data=spl_data
    event= load_data['event']['problem_id']
    mapper={}
    mapper["event_id"]= event_mapper[event]
    mapper ["name"]= spl_data["username"]
    mapper ["time"]= spl_data["time"]
    mapper["action"] = spl_data["event_type"]
    mapper["country"]= spl_data["augmented"]["country_code"]
    mapper["event_source"]=spl_data["event_source"]
    mapper["session"]= spl_data["session"]
    final_list.append(mapper)

def event_set_3(spl_data):
    load_data=spl_data["event"]
    data=json.loads(load_data)
    event= data["problem"]
    mapper={}
    mapper["event_id"]= event_mapper[event]
    mapper ["name"]= spl_data["username"]
    mapper ["time"]= spl_data["time"]
    mapper["action"] = spl_data["event_type"]
    mapper["country"]= spl_data["augmented"]["country_code"]
    mapper["event_source"]=spl_data["event_source"]
    mapper["session"]= spl_data["session"]
    final_list.append(mapper)

def event_set_4(spl_data):
    load_data=spl_data
    event= load_data['event']['mode']
    mapper={}
    mapper["event_id"]= event_mapper[event]
    mapper ["name"]= spl_data["username"]
    mapper ["time"]= spl_data["time"]
    mapper["action"] = spl_data["event_type"]
    mapper["country"]= spl_data["augmented"]["country_code"]
    mapper["event_source"]=spl_data["event_source"]
    mapper["session"]= spl_data["session"]
    final_list.append(mapper)

def event_set_5(spl_data):
    load_data=spl_data["event"]
    data=json.loads(load_data)
    event= data['type']
    mapper={}
    mapper["event_id"]= event_mapper[event]
    mapper ["name"]= spl_data["username"]
    mapper ["time"]= spl_data["time"]
    mapper["action"] = spl_data["event_type"]
    mapper["country"]= spl_data["augmented"]["country_code"]
    mapper["event_source"]=spl_data["event_source"]
    mapper["session"]= spl_data["session"]
    final_list.append(mapper)

def event_set_6(spl_data):
    oad_data=spl_data
    event= load_data['specialdeactivation']
    mapper={}
    mapper["event_id"]= event_mapper[event]
    mapper ["name"]= spl_data["username"]
    mapper ["time"]= spl_data["time"]
    mapper["action"] = spl_data["event_type"]
    mapper["country"]= spl_data["augmented"]["country_code"]
    mapper["event_source"]=spl_data["event_source"]
    mapper["session"]= spl_data["session"]
    final_list.append(mapper)




start_time= time.time()
event_mapper
final_list=[] #contains all the list of dictionary
with open("BerkeleyX_Stat_2.1x_1T2014-events.log") as data:
    for line in data.readlines():
        load_data=json.loads(line)
        event_type=load_data["event_type"]
        if event_type in ignore_list:
            pass
        elif event_type[0]== "/":
            mapper={}
            mapper["event_id"]=event_mapper[event_type]
            mapper ["name"]= load_data["username"]
            mapper ["time"]= load_data["time"]
            mapper["action"] = None
            mapper["country"]= load_data["augmented"]["country_code"]
            mapper["event_source"]=load_data["event_source"]
            mapper["session"]= load_data["session"]
            final_list.append(mapper)

        elif event_type == "problem_check":
            problem_check_event(load_data)

        elif event_type in event_set_1_list:
            event_set_1(load_data)

        elif event_type in event_set_2_list:
            event_set_2 (load_data)

        elif event_type in event_set_3_list:
            event_set_3 (load_data)

        elif event_type in event_set_4_list:
            event_set_4 (load_data)

        elif event_type in event_set_5_list:
            event_set_5 (load_data)

        elif event_type in event_set_6_list:
            event_set_6(load_data)



end_time=time.time()
time_taken= (end_time - start_time)


def csv_write(filename, dict_name)
    csv_file=open(filename, 'wb')
    writer=csv.writer(csv_file)
with open("event_map.json", "w") as fp:
    json.dump(event_mappings, fp)

print (time_taken)


'''def problem_check_event(spl_data, counte:r):
    counter=counter
    load_data=spl_data
    for i in load_data["event"]["correct_map"]:
        a= load_data["event"]["correct_map"][i]["correctness"]
        b= i
        c= i + "-" + a
        event_mappings[c]= counter
        counter +=1
    return(counter)

'''
