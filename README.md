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
# export GOOGLE_CLIENT_SECRET_NAME=projects/693032250063/secrets/webapp_google_client_secret
export SPREADSHEET_ID=1zdI_qP4Vj77Gx2mSNMJw67EXKZAljMkBgux3DCpi0O0
export GOOGLE_CLIENT_SECRET_NAME=projects/693032250063/secrets/g_auth_kz_pmt
export INVOICE_API_KEY=my-secret-key
export FLASK_DEBUG=1
python main.py
curl -X POST http://localhost:8080/log-invoice/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $INVOICE_API_KEY" \
  -d '{
    "line_items": [
      ["", "Трубы профильные 40х40х1,2", "1,133", "т", "482000", "546106", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Трубы профильные 80х80х5 по ГОСТ 8639-82", "1,374", "т", "447000", "614178", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Резка металла", "10", "шт", "200", "2000", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Трубы профильные 100х50х3 ГОСТ 8645-68", "0,925", "т", "437000", "404225", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Двутавр 25Б1 Ст3/С255", "6,816", "т", "622000", "4239552", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Уголок 75х5 ст3сп-5", "0,348", "т", "387000", "134676", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Резка металла", "5", "шт", "210", "1050", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Двутавр 12 Б1 Ст3/С255", "0,106", "т", "737000", "78122", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Резка металла", "1", "шт", "330", "330", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Трубы профильные 80х40х3 ГОСТ 8645-68", "0,316", "т", "437000", "138092", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"],
      ["", "Резка металла", "22", "шт", "660", "14520", "2025-06-27T04:06:11.034973", "ТОО \"Лидер-Металл\"", "081240002981", "14673"]
    ],
    "order": [
      ["081240002981", "KZ62601A861003570421", "ТОО \"Лидер-Металл\"", "17", "710", "Счет на оплату № Т-14673 от 25 июня 2025 г.", "6172851", "25.06.2025"]
    ]
  }'

```
The `INVOICE_API_KEY` value acts as a shared secret. Clients must send this
value in the `X-Api-Key` header on each request. Requests without the correct
header will receive a `403 Forbidden` response.

Make sure you have authenticated with the Google Cloud SDK so the
application can access Secret Manager locally:
```bash
gcloud auth application-default login
```

## Deploying to Cloud Run
Use Cloud Build to build the container and deploy:
```bash
gcloud builds submit --config cloudbuild.yaml --substitutions _REGION=europe-west1,_SERVICE=kz-pmt-automation
```
Then deploy the resulting image to Cloud Run.

## Google Sheets setup

The service account retrieved from Secret Manager must have edit access to the
target spreadsheet. Share the spreadsheet with the service account's email
address. The spreadsheet should contain two sheets named `bank_input` and
`orders`, which are used when appending data from the API.

## Using with Custom GPT Actions

The included `openapi.yaml` defines an `ApiKeyAuth` scheme so Custom GPTs can
authenticate by sending an `X-Api-Key` header. Import this file into the GPT
builder and configure the Action's authentication to use your key:

1. Select **API Key** and choose **Custom** location.
2. Enter `X-Api-Key` as the header name and paste the value of
   `INVOICE_API_KEY` used on Cloud Run.
3. Save and test the Action. A successful request will return:

   ```json
   {"status": "success", "message": "Logged to Google Sheets."}
   ```

## OAuth proxy setup

The service also exposes two helper endpoints for OAuth 2.0 flows used by
Custom GPT Actions:

* `/oauth2/auth` – redirects the user to Google's consent screen.
* `/oauth2/token` – exchanges the authorization code for an access token.

Set the following environment variables when deploying to Cloud Run so the
proxy can call Google's OAuth endpoints:

```bash
export GOOGLE_OAUTH_CLIENT_ID=<your-client-id>
export GOOGLE_OAUTH_CLIENT_SECRET=<your-client-secret>
export OAUTH_REDIRECT_URI=<OpenAI-callback-URL>
```

`OAUTH_REDIRECT_URI` should match the callback URL provided by the GPT Builder.
All three URLs (your API host, Authorization URL and Token URL) will then share
the same `*.run.app` domain, satisfying the builder's domain requirement.
