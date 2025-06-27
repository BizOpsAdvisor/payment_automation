import os
import json
from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import secretmanager

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
SERVICE_ACCOUNT_FILE = os.environ.get(
    'GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json'
)
SECRET_NAME = os.environ.get(
    'GOOGLE_CLIENT_SECRET_NAME',
    'projects/693032250063/secrets/webapp_google_client_secret',
)


@lru_cache()
def _load_credentials():
    """Load service account credentials.

    Credentials are fetched from Secret Manager if ``SECRET_NAME`` is
    configured, otherwise they are read from ``SERVICE_ACCOUNT_FILE``.
    """
    if SECRET_NAME:
        client = secretmanager.SecretManagerServiceClient()
        name = f"{SECRET_NAME}/versions/latest"
        response = client.access_secret_version(name=name)
        info = json.loads(response.payload.data.decode("UTF-8"))
        return service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )

    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


@lru_cache()
def _get_sheet():
    credentials = _load_credentials()
    service = build("sheets", "v4", credentials=credentials)
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
