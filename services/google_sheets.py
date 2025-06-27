import os
import json
from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import secretmanager

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
# Full resource name for the Secret Manager secret containing the service
# account JSON. This value is required.
SECRET_NAME = os.environ.get("GOOGLE_CLIENT_SECRET_NAME")


@lru_cache()
def _load_credentials():
    """Load service account credentials.

    Credentials are fetched from Secret Manager using ``GOOGLE_CLIENT_SECRET_NAME``.
    """
    if not SECRET_NAME:
        raise RuntimeError("GOOGLE_CLIENT_SECRET_NAME environment variable not set")

    client = secretmanager.SecretManagerServiceClient()
    name = f"{SECRET_NAME}/versions/latest"
    response = client.access_secret_version(name=name)
    info = json.loads(response.payload.data.decode("UTF-8"))
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


@lru_cache()
def _get_sheet():
    """Return a cached Google Sheets service client."""
    credentials = _load_credentials()
    service = build("sheets", "v4", credentials=credentials)
    return service.spreadsheets()


def log_invoice(*, line_items=None, order=None):
    """Log invoice data to Google Sheets."""
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
