from __future__ import print_function
import pickle
import os.path
from datetime import date, datetime, timedelta

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID of TimeSheet spreadsheet.
SPREADSHEET_ID = '1IXKWLBVHitg2B1W1dse3FUOkLM8g1UnbDPS4Eseq1mk'  # TimeSheet table
COL_DESCR = 'A'
COL_START = 'B'
COL_STOP = chr(ord(COL_START) + 1)
COL_TIME = chr(ord(COL_STOP) + 1)
COL_RANGE = chr(ord(COL_TIME) + 1)


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


def update_range(sheet, range):
    data = [[range]]
    body = {'values': data}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range=f'Лист1!{COL_RANGE}2:{COL_RANGE}2', body=body).execute()
    return result


def get_range(sheet):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f'Лист1!{COL_RANGE}2:{COL_RANGE}2').execute()
    range = result['values'][0][0]
    return range


def a1_range_to_tuple(a1_range):
    return a1_range[0:8], a1_range[8], a1_range[9:]


def to_column_range(range, col_name):
    t = a1_range_to_tuple(range)
    return t[0] + col_name + t[2]


def to_next_row_range(a1_range):
    t = a1_range_to_tuple(a1_range)
    range_row_num = int(t[2])
    range_row_num += 1
    return t[0] + t[1] + str(range_row_num)


def get_next_range(a1_range):
    if COL_START in a1_range:
        range = to_column_range(a1_range, COL_STOP)
    else:
        range = to_column_range(a1_range, COL_START)
        range = to_next_row_range(range)
    return range


def get_grid_range(a1_range: str):
    _tuple = a1_range_to_tuple(a1_range)
    _start_row_index = int(_tuple[2]) - 1
    _end_row_index = _start_row_index + 1
    _start_column_index = ord(_tuple[1].upper()) - 65
    _end_column_index = _start_column_index + 1
    _grid_range = {
        'sheet_id': 0,
        'startRowIndex': _start_row_index,
        'endRowIndex': _end_row_index,
        'startColumnIndex': _start_column_index,
        'endColumnIndex': _end_column_index
    }
    return _grid_range


def get_formula_request(formula: str, range):
    _request = {
        "repeatCell": {
            "range": range,
            "cell": {
                "userEnteredValue": {
                    "formulaValue": formula
                }
            },
            "fields": 'userEnteredValue'
        }
    }
    return _request


def set_formula(formula: str, a1_range):
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()
    formula_range = get_grid_range(a1_range)
    formula_request = get_formula_request(formula, formula_range)
    requests = [formula_request]

    body = {'requests': requests}
    result = srv.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,  body=body).execute()
    return result


def _set_task_descr(sheet, descr):
    range = get_range(sheet)
    range = to_next_row_range(range)
    range = to_column_range(range, COL_DESCR)
    data = [[descr]]
    body = {'values': data}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range=range, body=body).execute()
    return result


def _start_task(sheet, range):
    now = google_now()
    data = [[now]]
    body = {'values': data}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range=range, body=body).execute()
    return result


def _stop_task(sheet, range):
    now = google_now()
    data = [[now]]
    body = {'values': data}
    result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range=range, body=body).execute()
    return result


def _set_task_duration(srv, range):
    duration_range = get_grid_range(range)
    duration_range["startColumnIndex"] = ord(COL_TIME) - 65
    duration_range["endColumnIndex"] = duration_range['startColumnIndex'] + 1
    row_num = duration_range["startRowIndex"]+1
    formula = f'={COL_STOP}{row_num} - {COL_START}{row_num}'
    formula_request = get_formula_request(formula, duration_range)
    requests = [formula_request]

    body = {'requests': requests}
    result = srv.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    return result


def set_task_descr(descr):
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()
    res = _set_task_descr(sheet, descr)
    if 'updates' in res and 'updatedRange' in res['updates']:
        _updated_range = res['updates']['updatedRange']
        update_range(sheet, _updated_range)
    return res


def start_task():
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()
    range = get_range(sheet)
    range = to_column_range(range, COL_START)
    res = _start_task(sheet, range)
    update_range(sheet, range)
    return res


def stop_task():
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()
    range = get_range(sheet)
    
    range = to_column_range(range, COL_STOP)
    res = _stop_task(sheet, range)
    update_range(sheet, range)
    _set_task_duration(srv, range)
    return res


# if __name__ == '__main__':
    # res = set_task_descr('Приготовить плов')
    # res = start_task()
    # res = stop_task()
    # print(res)

