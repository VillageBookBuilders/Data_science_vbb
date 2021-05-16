import pandas as pd 
import random
import regex
import math
from collections import namedtuple
from datetime import date, datetime, timedelta

timeslot = namedtuple('Interval', ['start', 'end'])
id = 0

INPUT_PATH = "D:\Downloads\drive-download-20210410T013418Z-001\Mukono, Uganda.xlsx" # path to input excel file
DURATION_FILE_PATH = "D:\Downloads\drive-download-20210410T013418Z-001\meet_data\Mukono.csv" # output of file containing duration info
AUGMENTED_MEET_FILE_PATH = "D:\Downloads\drive-download-20210410T013418Z-001\meet_data\Mukono.csv" # output of original file with id tag added

def is_mentor(email):
    if pd.isnull(email):
        return True
    domain = email[email.index('@') + 1 : ]
    if (domain == "villagebookbuilders.org" and email != "brett@villagebookbuilders.org") or email == "mpmukono@villagementors.org": # is a mentee; Brett and mpmukono are special cases (a mentor and mentee email, respectively)
        return False
    else:
        return True # default to assuming a user is a mentor


def get_meet_ids(df):
    meetings = df["Meeting Code"].unique()
    return meetings


def meeting_by_id(id):
    meets = []
    meets.append(pd.DataFrame(df.loc[df["Meeting Code"] == id]))
    return meets


def utc_to_time(utc):
    time = utc[utc.index('T') + 1 : ]
    time_obj = datetime.strptime(time, "%H:%M:%S")
    return time_obj


def merge_times(times): # merge mentors or mentees if more than one of each is present in a meeting at the same time
    times.sort()
    for i in range(len(times) - 1):
        first_end = times[i][1]
        next_start = times[i + 1][0]

        if first_end.time() > next_start.time():
            new_start = min(times[i].start, times[i+1].start)
            new_end = max(times[i].end, times[i+1].end)

            new_slot = timeslot(new_start, new_end)
            first_time = times[i]
            next_time = times[i+1]
            times.remove(first_time)
            times.remove(next_time)
            times.append(new_slot)
            break
            merge_times(times)
    return times


def get_overlap(first, second): # returns whatever overlap may exist between meetings
    return max(0, (min(first[1], second[1]) - max(first[0], second[0])).total_seconds())


def calculate_overlap(meeting):
    mentor_intervals = []
    student_intervals = []
    names = meeting["Participant Identifier"].unique()

    for row in meeting.iterrows(): # for each meeting, split into mentor/mentee arrays and merge overlapping times within each array
        start = row[1]['UTC']
        start = utc_to_time(start)
        end = start + timedelta(0,row[1]['Duration'])
        timepair = timeslot(start, end)
        name = row[1]['Participant Identifier']
        if is_mentor(name):
            mentor_intervals.append(timepair)
        else:
            student_intervals.append(timepair)
    mentor_intervals = merge_times(mentor_intervals)
    student_intervals = merge_times(student_intervals)

    overlap = 0
    for mentor_interval in mentor_intervals:
        for student_interval in student_intervals:
            overlap += get_overlap(mentor_interval, student_interval)
    return overlap


df = pd.read_excel(INPUT_PATH) 
unique_meets = get_meet_ids(df)
df["id"] = 0

new_df = [["Meeting Code", "Tutoring Time (s)", "ID"]] # columns for new spreadsheet

for meet_id in unique_meets:
    meets = meeting_by_id(meet_id)

    for meet in meets:
        overlap = calculate_overlap(meet)
        id = id
        new_df.append([meet_id, overlap, id])
        df.loc[df['Meeting Code'].eq(meet_id),'id'] = id # Find all values in original DF where meeting code is the same as the current meet; replace filler ID with current ID value corresponding to row in the new table
        id += 1

pd.DataFrame(new_df).to_csv(DURATION_FILE_PATH)
df.to_csv(AUGMENTED_MEET_FILE_PATH)
