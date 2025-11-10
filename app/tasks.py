# app/tasks.py
import base64
import re
import sqlite3
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
from bs4 import BeautifulSoup
from app.celery_app import celery_app
from app.config import Config
import os


# --- Helper for Gmail API Authentication ---
def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    print("Current working Dir", os.getcwd())
    print("GMAIL_CREDENTIALS_FILE path", Config.GMAIL_CREDENTIALS_FILE)
    if os.path.exists(Config.GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(Config.GMAIL_TOKEN_FILE, Config.GMAIL_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                Config.GMAIL_CREDENTIALS_FILE, Config.GMAIL_SCOPES)
            # creds = flow.run_local_server(port=0)
            creds = flow.run_console()


        # Save the credentials for the next run
        with open(Config.GMAIL_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())


    service = build('gmail', 'v1', credentials=creds)
    return service


# --- Task 1: Check Gmail for Invoices ---
@celery_app.task(name='app.tasks.check_gmail_for_invoices', queue='gmail_queue')
def check_gmail_for_invoices():
    print("Checking Gmail for new invoice emails...")
    try:
        service = get_gmail_service()
        # Query for unread emails with the specific subject
        query = f"is:unread subject:\"{Config.GMAIL_INVOICE_SUBJECT}\""
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])


        if not messages:
            print("No new invoice emails found.")
            return
        print(f"Found {len(messages)} new invoice emails.")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            # Extract email body
            email_body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        email_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                        html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        soup = BeautifulSoup(html_body, 'html.parser')
                        email_body = soup.get_text()  # Extract plain text from HTML
                        break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                email_body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        if email_body:
            print(f"Extracted email body for message ID {message['id']}. Sending to parser task.")
            # Mark email as read after processing
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
            parse_invoice_email.apply_async(args=[email_body], queue='parser_queue')
        else:
            print(f"Could not extract body for message ID {message['id']}. Skipping.")
    except HttpError as error:
        print(f"An error occurred with Gmail API: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Task 2: Parse Invoice Email ---
@celery_app.task(name='app.tasks.parse_invoice_email', queue='parser_queue')
def parse_invoice_email(email_body):
    print("Parsing invoice email body...")
    invoice_id = None
    invoice_amount = None
    # Example parsing logic (adjust regex as needed for your specific email format)
    # Assuming email body contains lines like:
    # "Invoice ID: INV-2023-001"
    # "Amount Due: $150.75"
    # Regex for Invoice ID
    id_match = re.search(r"Invoice ID:\s*([A-Z0-9-]+)", email_body, re.IGNORECASE)
    if id_match:
        invoice_id = id_match.group(1).strip()
    # Regex for Invoice Amount (can handle currency symbols, commas, decimals)
    amount_match = re.search(r"Amount Due:\s*[$€£]?\s*([\d,]+\.?\d{0,2})", email_body, re.IGNORECASE)
    if amount_match:
        invoice_amount = float(amount_match.group(1).replace(',', ''))


    if invoice_id and invoice_amount is not None:
        print(f"Parsed - Invoice ID: {invoice_id}, Amount: {invoice_amount}. Sending to DB saver task.")
        save_invoice_to_db.apply_async(args=[invoice_id, invoice_amount], queue='db_saver_queue')
    else:
        print(f"Failed to parse invoice ID or amount from email body: {email_body[:200]}...")  # Log first 200 chars
        if not invoice_id:
            print("Invoice ID not found.")
        if invoice_amount is None:
            print("Invoice Amount not found.")


# --- Task 3: Save Invoice to DB ---
@celery_app.task(name='app.tasks.save_invoice_to_db', queue='db_saver_queue')
def save_invoice_to_db(invoice_id, invoice_amount):
    print(f"Saving Invoice ID: {invoice_id}, Amount: {invoice_amount} to database...")
    try:
        db_path = Config.DATABASE_URI.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        # conn = sqlite3.connect(Config.DATABASE_URI)
        cursor = conn.cursor()
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT UNIQUE,
                amount REAL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


        cursor.execute("INSERT INTO invoices (invoice_id, amount) VALUES (?, ?)",
                       (invoice_id, invoice_amount))
        conn.commit()
        conn.close()
        print(f"Successfully saved Invoice ID: {invoice_id} to database.")
    except sqlite3.IntegrityError:
        print(f"Invoice with ID {invoice_id} already exists in the database. Skipping.")
    except Exception as e:
        print(f"Error saving invoice to DB: {e}")
