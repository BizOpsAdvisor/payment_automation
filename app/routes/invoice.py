import logging
import os
from flask import Blueprint, request, jsonify, abort

from services.google_sheets import log_invoice

invoice_bp = Blueprint("invoice", __name__)
logger = logging.getLogger(__name__)


API_KEY = os.environ.get("INVOICE_API_KEY")
if not API_KEY:
    raise RuntimeError("INVOICE_API_KEY not set")

@invoice_bp.route('/', methods=['POST'])
def create_invoice():
    if request.headers.get("X-Api-Key") != API_KEY:
        abort(403)  # Forbidden if the key doesn’t match
    data = request.get_json() or {}
    logger.info("Received invoice payload: %s", data)
    line_items = data.get("line_items", [])
    order = data.get("order", [])

    try:
        log_invoice(line_items=line_items, order=order)
        logger.info("Data logged to Google Sheets successfully")
        return (
            jsonify({"status": "success", "message": "Logged to Google Sheets."}),
            200,
        )
    except Exception as exc:
        logger.exception("Failed to log invoice: %s", exc)
        return jsonify({"status": "error", "message": str(exc)}), 500
