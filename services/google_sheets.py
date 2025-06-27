import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')


def _get_sheet():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service.spreadsheets()


def log_invoice(*, line_items=None, order=None):
    sheet = _get_sheet()

    if line_items:
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='bank_input!A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': line_items},
        ).execute()

    if order:
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='orders!A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [order]},
        ).execute()
