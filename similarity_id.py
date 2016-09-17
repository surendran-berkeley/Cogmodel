import json
import time

event_mappings ={}

spl_event_types=['speed_change_video', 'page_close', 'problem_show', 'edx.user.settings.changed', 'edx.course.enrollment.deactivated', 'show_transcript', 'hide_transcript', 'seq_prev', 'edx.forum.searched', 'list-forum-mods', 'seq_next', 'reset_problem', 'get-student-progress-page', 'video_hide_cc_menu', 'seek_video', 'save_problem_success', 'list-staff', 'edx.course.enrollment.upgrade.succeeded', 'showanswer', 'reset-student-attempts', 'load_video', 'add-forum-mod', 'add-forum-admin', 'seq_goto', 'play_video', 'problem_check_fail', 'save_problem_fail', 'reset_problem_fail', 'rescore-student-submission', 'stop_video', 'edx.course.enrollment.mode_changed', 'video_show_cc_menu', 'problem_check', 'pause_video', 'list-forum-admins', 'edx.course.enrollment.activated']

event_set_1_list=['hide_transcript', 'speed_change_video', 'video_hide_cc_menu', 'seq_prev', 'seq_goto', 'show_transcript', 'load_video', 'seq_next', 'video_show_cc_menu', 'stop_video', 'pause_video', 'play_video']


event_set_2_list=['save_problem_success', 'reset_problem', 'problem_check_fail', 'save_problem_fail', 'showanswer'] #removed problem_check and have created a seperate function to handle the same

event_set_3_list=['problem_show']

event_set_4_list=['edx.course.enrollment.mode_changed', 'edx.course.enrollment.activated']

event_set_5_list= ['seek_video']
event_set_6_list= ['edx.course.enrollment.deactivated']

ignore_list= ["edx.course.enrollment.upgrade.succeeded", "list-staff", "get-student-progress-page","reset_problem_fail", "rescore-student-submission", "source", "edx.forum.searched", "list-forum-admins","list-forum-mods", "edx.user.settings.changed", "reset-student-attempts","add-forum-admin", "add-forum-mod"]

# problem_check_state={}



def problem_check_event(spl_data, counter):
    counter=counter
    load_data=spl_data
    even=load_data["event_type"]
    for i in load_data["event"]["correct_map"]:
        b= i
        if i not in event_mappings:
            event_mappings[i]= []
            counter+=1
        else:
            if event_type not in event_mappings[i]:
                event_mappings[i].append(load_data["event_type"])
            else:
                pass

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
    event= data['type']
    return event

def event_set_6(spl_data):
    oad_data=spl_data
    event= load_data['specialdeactivation']
    return event




start_time= time.time()
with open("BerkeleyX_Stat_2.1x_1T2014-events.log") as data:
    counter=1
    print (counter)
    for line in data.readlines():
        load_data=json.loads(line)
        event_type=load_data["event_type"]

        if event_type[0]== "/" :
            if event_type  not in event_mappings:
                a= event_type
                event_mappings[a]= []
                counter+=1
            else:
                pass
        elif event_type in ignore_list:
            pass
        elif event_type == "problem_check":
            a=problem_check_event(load_data, counter)
            counter = a

        elif event_type in event_set_1_list:
            a = event_set_1(load_data)
            if a not in event_mappings:
                event_mappings[a] =[]
                counter+=1
            else:
                if event_type not in event_mappings[a]:
                    event_mappings[a].append(event_type)
                else:
                    pass


        elif event_type in event_set_2_list:
            a = event_set_2 (load_data)
            if a not in event_mappings:
                event_mappings[a] =[]
                counter+=1
            else:
                if event_type not in event_mappings[a]:
                    event_mappings[a].append(event_type)
                else:
                    pass



        elif event_type in event_set_3_list:
            a = event_set_3 (load_data)
            if a not in event_mappings:
                event_mappings[a] =[]
                counter+=1
            else:
                if event_type not in event_mappings[a]:
                    event_mappings[a].append(event_type)
                else:
                    pass



        elif event_type in event_set_4_list:
            a = event_set_4 (load_data)
            if a not in event_mappings:
                event_mappings[a] =[]
                counter+=1
            else:
                if event_type not in event_mappings[a]:
                    event_mappings[a].append(event_type)
                else:
                    pass


        elif event_type in event_set_5_list:
            a = event_set_5 (load_data)
            if a not in event_mappings:
                event_mappings[a] =[]
                counter+=1
            else:
                if event_type not in event_mappings[a]:
                    event_mappings[a].append(event_type)
                else:
                    pass

        elif event_type in event_set_6_list:
            a = event_type
            if a not in event_mappings:
                event_mappings[a] =[]
                counter+=1
            else:
                if event_type not in event_mappings[a]:
                    event_mappings[a].append(event_type)
                else:
                    pass


end_time=time.time()
time_taken= (end_time - start_time)

event_map_2={}
for i in event_mappings:
    if len(event_mappings[i])==0:
        pass
    else:
        event_map_2[i]= event_mappings[i]
with open("event_map.json", "w") as fp:
    json.dump(event_map_2, fp)

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
