import pandas as pd
import numpy as np
import itertools
import os.path
import csv
import json
from datetime import datetime

#from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
#    FileTransferSpeed, FormatLabel, Percentage, \
#    ProgressBar, ReverseBar, RotatingMarker, \
#    SimpleProgress, Timer


def load_dle_data(filename,d_stu,d_cor):
    if os.path.isfile('.' + filename + '.X.npy'):
        return np.load('.' + filename + '.X.npy'), np.load('.' + filename + '.sw.npy')
    
    df=pd.read_csv(filename,delimiter=',')
    
    # array of rows totals per unique student
    stu=[sum(1 for _ in group) for key, group in itertools.groupby(df[d_stu]) if key]

    # this is how we handle variable length sequences
    # by masking in the form of 0 weighted loss after the sequence ends
    sw = np.zeros([len(stu), max(stu)],dtype='bool')
    for i in range(len(stu)):
        sw[i,0:stu[i]] = 1
                   
    # create a matrix based on the longest length individual student sequence
    X = np.zeros([len(stu), max(stu), 1],dtype='int8')
    S = df[d_stu].unique()

    s1_dict = dict(zip(S,np.zeros(len(S),dtype='int16')))
    s2_dict = dict(zip(S,range(len(S))))    

    # for each row in df, insert the response into the respective student's seq
    widgets = ['Processed: ', Counter(), ' lines ',Percentage(), Bar(), ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=len(df)).start()
    for i in range(len(df)):
        X[s2_dict[df[d_stu][i]],s1_dict[df[d_stu][i]]] = df[d_cor][i]
        s1_dict[df[d_stu][i]] += 1
        pbar.update(i)

    rp = np.random.permutation(X.shape[0])
    X = X[[rp]]
    sw = sw[[rp]]

    np.save('.' + filename + '.X',X)
    np.save('.' + filename + '.sw',sw)
    
    return X, sw

def generate_sequences_from_edx(edx_event_log_file, event_types_to_drop, special_case_event_types, auto_policy_find = False, earliest_time = datetime.min, latest_time = datetime.max, minlen = 0):    
    """
    Returns:
    1. List of lists of student actions converted to indices (can be filtered according to times)
    2. Dictionary mapping of index to URL
    3. List of user ids corresponding to student actions
    4. List of datetimes associated with actions

    Configured to work on /mooc_v2/data/BerkeleyX_Stat_2.1x_1T2014-events.log
    
    Events are filtered according to https://docs.google.com/document/d/1t-A5i02wMExunBsKBUyHNP9_kRtAO_FqkFIoZUvkBGA/edit
    
    filename - filename
    event_types_to_drop - list of event_types to completely drop
    special_case_event_types: dictionary of special events that need specific order to grab what we consider to the string url

    Example of event_types_to_drop:
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

    Example of special_case_event_types:
    This dictionary is necessary to describe event types that do not have a direct URL to represent the action.
    When there is no direct URL, we instead must look into the json object for a specific ID or descriptor to serve as a placeholder for the URL. This placeholder should describe the action in some way.
    Different event types have different unique identifier, and as such different event types will have their IDs located in a different part of the json representation of the event/action.
    Each key represents the event type,
    Each value represents a list of dictionary look ups, taken in order from left to right. There is a special string 'jsonloads' that indicates that a json.loads call must be performed on the json object,
    becasue the json object is currently a string rather than a dictionary.

    So, for example, for hide_transcript, the list of 3 elements will first lookup the key 'event' in the current action reprsented as a dictionary. Then, after this lookup, json.loads is called on the corresponding value. Finally,
    the value for the key 'id' is looked up.

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

    """
    if auto_policy_find: #this means automatically assume that we can find a policy log file to infer start and end time of course. Then add 2 days both ways, and discount any dates outside of start / end +/- 2 days
        print("not implemented")
        print("will eventually set earliest_time and latest_time to values corresponding to those found in edx policy file")
        return 5/0

    event_mappings = {} #maps event_types to unique resource index
    student_sequences = {} #maps student user id to list of student resource indices
    student_times = {} #maps student user id to list of action times
#    if error_log: #error just means that the user id is '' (blank), so error_log is to keep track of students who are missing an id
#        missing_users = []
#    BUG_TESTING = []
    with open(edx_event_log_file) as data_file:
        unique_index = 1 #this will be resource index for the one-hot encoding
        for line in data_file.readlines():
            data = json.loads(line) #loads the current row as a dictionary (json object)
            event_type = data['event_type']
            user = data['username']
            time_element = data['time']
            #convert the inconsistently formatted edx time string into a datetime object
            if '+' in time_element:
                if '.' in time_element:
                    date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S.%f')
                else:
                    date_object = datetime.strptime(time_element[:-6], '%Y-%m-%dT%H:%M:%S')
            elif '.' in time_element:
                date_object = datetime.strptime(time_element, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date_object = datetime.strptime(time_element, '%Y-%m-%dT%H:%M:%S')
            #BUG_TESTING.append(date_object)
            #if the time is outside the date parameters, drop the event completely
            if date_object < earliest_time or date_object > latest_time:
                continue
            if user == '':
#                if error_log:
#                    missing_users.append(data)
                continue
            if user not in student_sequences:
                student_sequences[user] = []
                student_times[user] = []
            if event_type in event_types_to_drop:
                continue
            if event_type[0] == "/": #if the first character is a /, then it is a direct URL we can use as the action
                if event_type not in event_mappings:
                    event_mappings[event_type] = unique_index
                    unique_index += 1
                final_action = event_mappings[event_type] #final action should be a NUMBER associated with a certain event type            
            else:
                instructions = special_case_event_types[event_type] #grab the list of instructions (i.e. continuous lookups into the json object)
                instructions = list(instructions) #need to make a copy of the current list, since the while loop will pop / mutate
                action = data
                while instructions: #recursively pop the first element off instructions. if it is jsonloads, then perform a json loads. if it is anything else, simply do a lookup with that as a key. one special case for enrollment deactivation
                    current = instructions.pop(0) #this will be the first element in the instructions. it is usually a key, but it can also be the special string jsonloads to indicate that the current dictionary is actually a string that needs to be loaded.
                    if current == 'jsonloads':
                        action = json.loads(action)
                    elif current == 'specialdeactivation':
                        action = 'ENROLLMENT_DEACTIVATED'
                    else:
                        action = action[current]
                action = event_type + action
                if action not in event_mappings:
                    event_mappings[action] = unique_index
                    unique_index += 1
                final_action = event_mappings[action]
            student_sequences[user].append(final_action)
            student_times[user].append(date_object)

        #EDX DATA ISSUE: Some students are entered in ascending time order, and others are entered in descending time order. No idea why. So we need to order by time.
        correct_order_student_action = {}
        correct_time_order = {}
        bug_check_0 = 0
        bug_check_1 = 0
        for user_id, actionseq in student_sequences.iteritems():
            corresponding_times = student_times[user_id]
            paired_sequence = zip(actionseq, corresponding_times)
            correct_order = sorted(paired_sequence, key = lambda p: p[1])            
            correct_order_student_action[user_id] = [p[0] for p in correct_order]
            correct_time_order[user_id] = [p[1] for p in correct_order]
            if correct_time_order[user_id] == student_times[user_id]:
                bug_check_0 += 1
            else:
                bug_check_1 += 1
        print('equivalent times: ', str(bug_check_0))
        print('different order times: ', str(bug_check_1))

        final_output = [] #final output will just be a list of student sequences. user id is dropped from the final output
        justids = []
        final_times = [] #final times is a list of student times, corresponding to the sequences from final_output
        for userid, actionseq in correct_order_student_action.iteritems():
            if len(actionseq) < minlen:
                continue
            final_output.append(actionseq)
            justids.append(userid)
            final_times.append(correct_time_order[userid])
        to_return = []
        to_return.append(final_output)
        to_return.append(event_mappings)
        to_return.append(justids)
        to_return.append(final_times)
#        to_return.append(BUG_TESTING)
        return tuple(to_return)


def load_MOOC_assess_data(filename, maxlen):

    # load event log

    # filter out event types discussed in the google doc

    
    pass
