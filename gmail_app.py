import base64
import re
import datetime
import copy

class Gmail_App:
    gmail_service = None
    def __init__(self, gmail_service) -> None:
        self.gmail_service = gmail_service
    def get_bybit_label_id(self, name):
        labels = self.gmail_service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"] == name:
                return label["id"]
        return ""


    def get_bybit_messages(self):
        messages = list()

        bybit_label_id = self.get_bybit_label_id("Bybit Wallet")
        bybit_done_label_id = self.get_bybit_label_id("Bybit Wallet Done")

        threads = self.gmail_service.users().threads().list(userId="me", labelIds=[bybit_label_id]).execute().get("threads", [])
        
        for thread in threads:
            message = self.gmail_service.users().threads().get(userId="me", id=thread["id"]).execute().get("messages", [])[0]
            
            message_headers = message["payload"]["headers"]
            subject = list(filter(lambda header: header["name"] == "Subject", message_headers))[0]["value"]
            
            is_found = re.findall(r"\[Bybit\]\[Bybit\] P2P (Sell|Buy) Order: Completed", subject)
            if len(is_found) == 0:
                self.gmail_service.users().threads().modify(userId="me", id=thread["id"], body={"removeLabelIds": [bybit_label_id], "addLabelIds": [bybit_done_label_id]}).execute()
                continue
            else:
                bybit_transaction_type = is_found[0]
                messages.append({"data": message, "transaction_type": bybit_transaction_type})
            self.gmail_service.users().threads().modify(userId="me", id=thread["id"], body={"removeLabelIds": [bybit_label_id], "addLabelIds": [bybit_done_label_id]}).execute()
    
        return messages

    def extract_transaction(self, message, transaction_type):
        bybit_money_flow = "Income"
        if transaction_type == "Sell":
            bybit_money_flow = "Outcome"

        message_body = message["payload"]["parts"][0]["parts"][0]["body"]["data"]

        message_body = base64.urlsafe_b64decode(message_body).decode()

        fiat_amount = re.findall(r">- Fiat Amount: ([0-9]+) VND<", message_body)[0]
        fiat_amount = int(fiat_amount)
        order_id = re.findall(r">- Order ID: ([\*,0-9]+)<", message_body)[0]
        order_date = re.findall(r"Order Creation Time: ([0-9|-]+)", message_body)[0]

        [year, month, day] = map(lambda item: int(item), order_date.split("-"))

        order_date = datetime.date(year, month, day).strftime("%d-%b-%Y")

        return [order_date, fiat_amount, bybit_money_flow, f"Order ID: {order_id}"]
    
    def create_cash_transactions_from_bybit_transactions(self, bybit_transactions):
        cash_transactions = copy.deepcopy(bybit_transactions)
        for i in range(len(cash_transactions)):
            if cash_transactions[i][2] == "Income":
                cash_transactions[i][2] = "Outcome"
            else: 
                cash_transactions[i][2] = "Income"
        return cash_transactions