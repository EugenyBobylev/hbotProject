from __future__ import print_function
import pickle
import os.path
from datetime import date, datetime, timedelta

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1IXKWLBVHitg2B1W1dse3FUOkLM8g1UnbDPS4Eseq1mk'  # TimeSheet


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
    :return:
    """
    d: timedelta = datetime.now() - datetime(1899, 12, 30)
    return d.total_seconds()/86400


def google_datetime(user_datetime: datetime) -> float:
    """
    get date and time in google sheet format
    :param user_datetime:
    :return:
    """
    d: timedelta = user_datetime - datetime(1899, 12, 30)
    return d.total_seconds()/86400


def main():
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

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Лист1!A1:C1').execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(f'{row}')

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Лист1!A2').execute()
    values = result.get('values', [])

    _from = google_now()
    _to = _from + 2
    data = [[_from, _to, 2]]
    body = {'values': data}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                   valueInputOption='RAW', range='Лист1!A2', body=body).execute()
    print(result)


if __name__ == '__main__':
    main()
