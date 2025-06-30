import os
import json
import logging
from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import secretmanager

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

logger = logging.getLogger(__name__)


@lru_cache()
def _load_credentials():
    """Load service account credentials.

    Credentials are fetched from Secret Manager using ``GOOGLE_CLIENT_SECRET_NAME``.
    The secret name is read from the environment each time this function is called
    so that updated secrets can be used without restarting the interpreter.
    """
    secret_name = os.environ.get("GOOGLE_CLIENT_SECRET_NAME")
    if not secret_name:
        raise RuntimeError("GOOGLE_CLIENT_SECRET_NAME environment variable not set")

    logger.info("Loading credentials from Secret Manager: %s", secret_name)
    client = secretmanager.SecretManagerServiceClient()
    name = f"{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    info = json.loads(response.payload.data.decode("UTF-8"))
    logger.info("Loaded service account %s from %s", info.get("client_email"), secret_name)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


@lru_cache()
def _get_sheet():
    """Return a cached Google Sheets service client."""
    credentials = _load_credentials()
    logger.info("Building Google Sheets client")
    service = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )
    return service.spreadsheets()


def log_invoice(*, line_items=None, order=None):
    """Log invoice data to Google Sheets."""
    if not SPREADSHEET_ID:
        raise RuntimeError("SPREADSHEET_ID environment variable not set")

    sheet = _get_sheet()

    if line_items:
        logger.info("Appending %d rows to bank_input sheet", len(line_items))
        try:
            result = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range="bank_input!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": line_items},
            ).execute()
            logger.info("bank_input append result: %s", result.get("updates"))
        except HttpError as err:
            logger.error("Failed to append line items: %s", err)
            raise
    else:
        logger.info("No line items provided; skipping bank_input update")

    if order:
        logger.info("Appending 1 row to orders sheet")
        try:
            result = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range="orders!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": order},
            ).execute()
            logger.info("orders append result: %s", result.get("updates"))
        except HttpError as err:
            logger.error("Failed to append order: %s", err)
            raise
    else:
        logger.info("No order data provided; skipping orders update")
