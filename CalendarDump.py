from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

class google_apis:
    __webdev_cred = ''
    __mentor_cred = ''

    def __init__(self):
        scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.group',
        ]
        # SERVICE_ACCOUNT_FILE = os.path.join("", "service-acc.json")
        credentials = service_account.Credentials.from_service_account_file(
            'service-acc.json', scopes=scopes)
        self.__webdev_cred = credentials.with_subject(
            'webdevelopment@villagebookbuilders.org')
        self.__mentor_cred = credentials.with_subject(
            'mentor@villagebookbuilders.org')


    def calendar_data_arr(self):
        data_arr = [['Associated Calendar', 'Meet Link', 'Participants', 'Start Time', 'End Time', 'ID']]
        calendar_service = build('calendar', 'v3', credentials=self.__mentor_cred)
        ids = calendar_service.calendarList().list().execute()
        for calendar_list_entry in ids['items']:
            print(calendar_list_entry['summary'])
            list = calendar_service.events().list(calendarId=calendar_list_entry['id']).execute()
            flag = True
            for event in list['items']:
                if 'hangoutLink' in event and 'attendees' in event:
                    data_arr.append([calendar_list_entry['summary'],
                                    event['hangoutLink'], event['attendees'], event['start'], event['end'], event['id']])
        df = pd.DataFrame(data_arr)
        print(df)
        df.to_csv('CalendarMeets_15Apr21.csv')

api_obj = google_apis()
api_obj.calendar_data_arr()