import requests
import json
import uuid


def GetUserWallet(username):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletAccounts",
        "document": "WalletAccounts",
        "team_member_ID": "1256001",
        "function_ID": "ABCDE",
        "command": "fetch",
        "field": {
            "username": f"{username}",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---geting-user-wallet")
    # print(json_data)
    return json_data


def CreateUserWallet(username, email, balance=0, currency="usd"):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    unique_id = uuid.uuid4()
    account_no = str(unique_id)

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletAccounts",
        "document": "WalletAccounts",
        "team_member_ID": "1256001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "username": f"{username}",
            "email": f"{email}",
            "balance": balance,
            "currency": f"{currency}",
            "account_no": f"{account_no}",
        },
        "update_field": {},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("----creating-user-wallet------")
    # print(json_data)
    return json_data

def updateUserWallet(username,balance):

    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletAccounts",
        "document": "WalletAccounts",
        "team_member_ID": "1256001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "username": f"{username}",
        },
        "update_field": {
            "balance": balance
        },
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---updating-user-wallet")
    # print(json_data)
    return json_data



def CreateUserInfo(username, email,hashed_password,otp_key):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletUserinfos",
        "document": "WalletUserinfos",
        "team_member_ID": "1258001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "username": f"{username}",
            "email": f"{email}",
            "wallet_password": f"{hashed_password}",
            "otp":f"{otp_key}",
        },
        "update_field": {},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---creating-user-info-----")
    # print(json_data)
    return json_data


def GetUserInfo(field):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletUserinfos",
        "document": "WalletUserinfos",
        "team_member_ID": "1258001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": field,
        "update_field": {},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---getting-user-info-----")
    # print(json_data)
    return json_data


def UpdateUserInfo(username, hashed_password,otp_key):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletUserinfos",
        "document": "WalletUserinfos",
        "team_member_ID": "1258001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "username": f"{username}",
        },
        "update_field": {"wallet_password": f"{hashed_password}","otp":f"{otp_key}"},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---updating-user-info-----")
    # print(json_data)
    return json_data


def GetUserTransaction(field,command):
    print("field",field)
    print("command",command)
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletTransactions",
        "document": "WalletTransactions",
        "team_member_ID": "1257001",
        "function_ID": "ABCDE",
        "command": command,
        "field": field,
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---geting-user-transactions")
    # print(json_data)
    return json_data


def CreateUserTransaction(
    username, email,amount, payment_id, session_id, today, transaction_type, status, 
):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletTransactions",
        "document": "WalletTransactions",
        "team_member_ID": "1257001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "username": f"{username}",
            "email": f"{email}",
            "transaction_type": f"{transaction_type}",
            "status": f"{status}",
            "amount": f"{amount}",
            "payment_id": f"{payment_id}",
            "session_id": f"{session_id}",
            "date": f"{today}",
        },
        "update_field": {},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---creating-transacton-info-----")
    # print(json_data)
    return json_data


def updateUserTransaction(field,update_field):

    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletTransactions",
        "document": "WalletTransactions",
        "team_member_ID": "1257001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": field,
        "update_field": update_field,
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---updating-user-transaction")
    # print(json_data)
    return json_data



def CreatePayViaWallet(price, currency,callback_url,initialization_id):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletPayInitializations",
        "document": "WalletPayInitializations",
        "team_member_ID": "1259001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "price": price,
            "currency": f"{currency}",
            "callback_url": f"{callback_url}",
            "initialization_id":f"{initialization_id}"
        },
        "update_field": {},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---wallet-payment-initializing-----")
    # print(json_data)
    return json_data



def GetPayViaWallet(initialization_id):
    headers = {
        "content-type": "application/json",
    }

    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WalletPayInitializations",
        "document": "WalletPayInitializations",
        "team_member_ID": "1259001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": {
            "initialization_id":f"{initialization_id}"
        },
        "update_field": {},
        "platform": "bangalore",
    }

    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print("---get-payment-ini-----")
    # print(json_data)
    return json_data
