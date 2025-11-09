# app/config.py
class Config:
    # Celery configuration
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
# Gmail API Configuration
    # You'll need to create a project in Google Cloud Console, enable Gmail API,
    # and create OAuth 2.0 client credentials (Desktop app type).
    # Download the client_secret.json and rename it to credentials.json
    # and place it in the 'app' directory or specify the path here.
    GMAIL_CREDENTIALS_FILE = r'client_secret_celery.json' # Make sure this file is in the 'app' directory
    GMAIL_TOKEN_FILE = 'token.json' # This file will be generated after first authentication
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    GMAIL_INVOICE_SUBJECT = "Invoice details"
# Database configuration
    DATABASE_URI = 'sqlite:///data/invoices.db'
