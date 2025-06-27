from flask import Blueprint, request, jsonify

from services.google_sheets import log_invoice

invoice_bp = Blueprint('invoice', __name__)


@invoice_bp.route('/', methods=['POST'])
def create_invoice():
    data = request.get_json() or {}
    line_items = data.get('line_items', [])
    order = data.get('order', [])

    try:
        log_invoice(line_items=line_items, order=order)
        return jsonify({'status': 'success', 'message': 'Logged to Google Sheets.'}), 200
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500
