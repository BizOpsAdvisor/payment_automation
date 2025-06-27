from flask import Flask
from app.routes.invoice import invoice_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(invoice_bp, url_prefix='/log-invoice')
    return app
