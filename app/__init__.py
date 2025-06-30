from flask import Flask


def create_app():
    """Application factory."""
    app = Flask(__name__)

    from .routes.invoice import invoice_bp
    from .routes.oauth import oauth_bp

    app.register_blueprint(invoice_bp, url_prefix="/log-invoice")
    app.register_blueprint(oauth_bp)

    return app
