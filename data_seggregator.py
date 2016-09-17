stat2014exceptions = {}
stat2014exceptions['hide_transcript'] = ['event', 'jsonloads', 'id']
stat2014exceptions['pause_video'] = ['event', 'jsonloads', 'id'] 
stat2014exceptions['problem_check_fail'] = ['event', 'problem_id'] 
stat2014exceptions['save_problem_fail'] =  ['event', 'problem_id']
stat2014exceptions['showanswer'] = ['event', 'problem_id'] 
stat2014exceptions['problem_show'] = ['event', 'jsonloads', 'problem']
stat2014exceptions['play_video'] = ['event', 'jsonloads', 'id'] 
stat2014exceptions['speed_change_video'] = ['event', 'jsonloads', 'id']
stat2014exceptions['video_hide_cc_menu'] =  ['event', 'jsonloads', 'id'] 
stat2014exceptions['edx.course.enrollment.mode_changed'] = ['event', 'mode'] 
stat2014exceptions['stop_video'] = ['event', 'jsonloads', 'id']
stat2014exceptions['show_transcript'] = ['event', 'jsonloads', 'id'] 
stat2014exceptions['reset_problem'] = ['event', 'problem_id']
stat2014exceptions['video_show_cc_menu'] = ['event', 'jsonloads', 'id'] 
stat2014exceptions['seek_video'] = ['event', 'jsonloads', 'type'] 
stat2014exceptions['save_problem_success'] = ['event', 'problem_id']
stat2014exceptions['edx.course.enrollment.activated'] = ['event', 'mode']
stat2014exceptions['seq_prev'] = ['event', 'jsonloads', 'id']
stat2014exceptions['edx.course.enrollment.deactivated'] = ['specialdeactivation']
stat2014exceptions['load_video'] = ['event', 'jsonloads', 'id']
stat2014exceptions['seq_next'] = ['event', 'jsonloads', 'id']
stat2014exceptions['seq_goto'] = ['event', 'jsonloads', 'id']
stat2014exceptions['problem_check'] = ['event', 'problem_id']

event_set_1=[]
event_set_2=[]
event_set_3=[]
event_set_4=[]
event_set_5=[]
event_set_6=[]

for key in stat2014exceptions:
    a= stat2014exceptions[key] 
    if a == ['event', 'jsonloads', 'id']:
        event_set_1.append(key)
    elif a == ['event', 'problem_id']:
        event_set_2.append(key)
    elif a == ['event', 'jsonloads', 'problem']:
        event_set_3.append(key)
    elif a == ['event', 'mode']:
        event_set_4.append(key)     
    elif a== ['event', 'jsonloads', 'type']:
        event_set_5.append(key)
    elif a == ['specialdeactivation']:
        event_set_6.append(key)

print (event_set_1)
print (event_set_2)
print (event_set_3)
print (event_set_4)
print (event_set_5)
print (event_set_6)