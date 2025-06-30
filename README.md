# Payment Automation Flask Service

This project exposes a single endpoint for logging invoice data to Google Sheets. It is designed to run on Google Cloud Run and built using Cloud Build.

## Structure
- `app/` – Flask application package
  - `routes/` – Blueprints
  - `__init__.py` – application factory
- `services/` – helper modules (Google Sheets integration)
- `main.py` – entrypoint used by Gunicorn or `flask run`
- `sample_data.py` – example payloads for testing
- `Dockerfile` and `cloudbuild.yaml` – container build configuration

## Running locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export SPREADSHEET_ID=1zdI_qP4Vj77Gx2mSNMJw67EXKZAljMkBgux3DCpi0O0
export GOOGLE_CLIENT_SECRET_NAME=projects/693032250063/secrets/webapp_google_client_secret
python main.py
```
Make sure you have authenticated with the Google Cloud SDK so the
application can access Secret Manager locally:
```bash
gcloud auth application-default login
```

## Deploying to Cloud Run
Use Cloud Build to build the container and deploy:
```bash
gcloud builds submit --config cloudbuild.yaml --substitutions _REGION=<region>,_SERVICE=<service-name>
```
Then deploy the resulting image to Cloud Run.

## Google Sheets setup

The service account retrieved from Secret Manager must have **edit** access to
the target spreadsheet. Share the spreadsheet with the service account's email
address. Ensure the spreadsheet contains two sheets named `bank_input` and
`orders`. These names are referenced directly in the code when appending data,
so they must match exactly. It also helps to create a header row in each sheet
before sending data so new rows are added below the headers.
