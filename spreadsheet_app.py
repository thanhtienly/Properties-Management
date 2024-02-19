import gspread
from googleapiclient import discovery

class Spreadsheet_App(gspread.client.Client):
    def __init__(self, spreadsheet_service: gspread.client.Client) -> None:
        self.spreadsheet_app = spreadsheet_service
    
    def add_transactions(self, spreadsheet_id, sheet_id, transactions):
        spreadsheet = self.spreadsheet_app.open_by_key(spreadsheet_id)
        sheet = spreadsheet.get_worksheet_by_id(sheet_id)
        sheet.append_rows(transactions)