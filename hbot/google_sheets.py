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


def append_duration(srv, next_range):
    duration_range = get_grid_range(next_range)
    duration_range["startColumnIndex"] = 2
    duration_range["endColumnIndex"] = 3
    row_num = duration_range["startRowIndex"]+1
    formula = f'=B{row_num} - A{row_num}'
    formula_request = get_formula_request(formula, duration_range)
    requests = [formula_request]

    body = {'requests': requests}
    result = srv.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
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


def a1_range_to_tuple(a1_range):
    return (a1_range[0:8], a1_range[8], a1_range[9:])


def get_next_range(range):
    range_tuple = a1_range_to_tuple(range)
    range_col_name = 'B' if range_tuple[1] == 'A' else 'A'
    range_row_num = int(range_tuple[2])
    if range_col_name == 'A':
        range_row_num += 1
    return range_tuple[0] + range_col_name + str(range_row_num)


def do_start_stop():
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()

    prev_range = get_range(sheet)
    next_range = get_next_range(prev_range)
    if 'A' in next_range:
        append_start(sheet, next_range)
    else:
        append_stop(sheet, next_range)
        append_duration(srv, next_range)
    update_range(sheet, next_range)


def set_format_cells():
    srv = get_google_sheet_srv()
    sheet = srv.spreadsheets()

    requests = []
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'endRowIndex': 100,
                'startColumnIndex': 2,
                'endColumnIndex': 2
            },
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {
                        'type': 'DATE',
                        'pattern': '[hh]:[mm]:[ss]'
                    }
                }
            },
            'fields': "userEnteredFormat.numberFormat"
        }
    })
    body = {'requests': requests}
    response = srv.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,  body=body).execute()
    print(response)


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


if __name__ == '__main__':
    do_start_stop()

    # result = set_formula(formula='=B2-A2', a1_range="'Лист1'!C2")
    # print(result)
