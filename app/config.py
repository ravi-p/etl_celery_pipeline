# app/config.py
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    GMAIL_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'client_secret_celery.json')
    # GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'client_secret_celery.json')
    # GMAIL_TOKEN_FILE = 'token.json' # This file will be generated after first authentication
    GMAIL_TOKEN_FILE = os.path.join(BASE_DIR, 'token.json') # This file will be generated after first authentication
    # GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    GMAIL_INVOICE_SUBJECT = "Invoice details"
# Database configuration
    DATABASE_URI = 'sqlite:///data/invoices.db'
