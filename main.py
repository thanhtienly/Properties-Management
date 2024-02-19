import os

from service import *
from dotenv import load_dotenv


def main():
    load_dotenv()
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    BYBIT_SHEET_ID = os.getenv("BYBIT_SHEET_ID")
    CASH_SHEET_ID = os.getenv("CASH_SHEET_ID")
    
    service = Service()
    gmail_app = service.gmail
    spreadsheet_app = service.spreadsheet

    messages = gmail_app.get_bybit_messages()
    bybit_transactions = list()

    for message in messages:
        data = gmail_app.extract_transaction(message["data"], message["transaction_type"])
        bybit_transactions.append(data)
    
    cash_transactions = gmail_app.create_cash_transactions_from_bybit_transactions(bybit_transactions)

    spreadsheet_app.add_transactions(SPREADSHEET_ID, BYBIT_SHEET_ID, bybit_transactions)
    spreadsheet_app.add_transactions(SPREADSHEET_ID, CASH_SHEET_ID, cash_transactions)

    
main()