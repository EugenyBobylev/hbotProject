from __future__ import print_function
import time
import pickle
import os.path
from datetime import date, datetime, timedelta

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1IXKWLBVHitg2B1W1dse3FUOkLM8g1UnbDPS4Eseq1mk'  # TimeSheet table


# *********************** google sheet date time functions *******************************
def google_today() -> int:
    """
    get today date in google sheet format
    """
    d: timedelta = date.today() - date(1899, 12, 30)
    return d.days


def google_date(user_date: date) -> int:
    """
    get date in google sheet format (without time)
    """
    d: timedelta = user_date - date(1899, 12, 30)
    return d.days


def google_now() -> float:
    """
    get now timestamp in google sheet format
    """
    d: timedelta = datetime.now() - datetime(1899, 12, 30)
    return d.total_seconds()/86400


def google_datetime(user_datetime: datetime) -> float:
    """
    get date and time in google sheet format
    """
    d: timedelta = user_datetime - datetime(1899, 12, 30)
    return d.total_seconds()/86400


# ******************** google sheets functions *********************************
def get_google_sheet_srv():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service


def append_start(sheet, range):
    now = google_now()
    data = [[now]]
    body = {'values': data}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range=range, body=body).execute()
    return result


def append_stop(sheet, range):
    now = google_now()
    data = [[now]]
    body = {'values': data}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range=range, body=body).execute()
    return result


def update_range(sheet, range):
    data = [[range]]
    body = {'values': data}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range='Лист1!D2:D2', body=body).execute()
    return result


def get_range(sheet):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Лист1!D2:D2').execute()
    range = result['values'][0][0]
    return range


def to_tuple(range):
    return (range[0:8], range[8], range[9:])


def get_next_range(range):
    range_tuple = to_tuple(range)
    range_col_name = 'B' if range_tuple[1] == 'A' else 'A'
    range_row_num = int(range_tuple[2])
    if range_col_name == 'A':
        range_row_num += 1
    return range_tuple[0] + range_col_name + str(range_row_num)


if __name__ == '__main__':
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()

    prev_range = get_range(sheet)
    next_range = get_next_range(prev_range)
    if 'A' in next_range:
        result = append_start(sheet, next_range)
    else:
        result = append_stop(sheet, next_range)
    update_range(sheet, next_range)
