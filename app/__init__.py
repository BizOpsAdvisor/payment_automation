from flask import Flask


def create_app():
    """Application factory."""
    app = Flask(__name__)

    from .routes.invoice import invoice_bp
    app.register_blueprint(invoice_bp, url_prefix="/log-invoice")

    return app
