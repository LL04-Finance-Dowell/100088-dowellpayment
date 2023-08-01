import requests
import json


def DowellTransactionCreate(payment_id, session_id, desc, today):
    headers = {
        "content-type": "application/json",
    }
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "DowellTransactions",
        "document": "DowellTransactions",
        "team_member_ID": "1220001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "payment_id": f"{payment_id}",
            "session_id": f"{session_id}",
            "amount": "",
            "currency": "",
            "name": "",
            "email": "",
            "desc": f"{desc}",
            "date": f"{today}",
            "city": "",
            "state": "",
            "address": "",
            "postal_code": "",
            "country_code": "",
            "order_id": "",
            "status": "",
            "mail_sent": "False",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    print(response)
    json_data = json.loads(response.json())
    return json_data


def DowellTransactionUpdate(
    payment_id,
    amount,
    currency,
    name,
    email,
    city,
    state,
    address,
    postal_code,
    country_code,
):
    headers = {
        "content-type": "application/json",
    }
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "DowellTransactions",
        "document": "DowellTransactions",
        "team_member_ID": "1220001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "payment_id": f"{payment_id}",
        },
        "update_field": {
            "amount": f"{amount}",
            "currency": f"{currency}",
            "name": f"{name}",
            "email": f"{email}",
            "city": f"{city}",
            "state": f"{state}",
            "address": f"{address}",
            "postal_code": f"{postal_code}",
            "country_code": f"{country_code}",
            "order_id": f"{payment_id}",
            "status": "succeeded",
            "mail_sent": "True",
        },
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


def GetDowellTransaction(payment_id):
    headers = {
        "content-type": "application/json",
    }
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "DowellTransactions",
        "document": "DowellTransactions",
        "team_member_ID": "1220001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": {
            "payment_id": f"{payment_id}",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)
    return json_data


def PublicTransactionCreate(payment_id, session_id, desc, today):
    headers = {
        "content-type": "application/json",
    }
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "PublicTransactions",
        "document": "PublicTransactions",
        "team_member_ID": "1221001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "payment_id": f"{payment_id}",
            "session_id": f"{session_id}",
            "amount": "",
            "currency": "",
            "name": "",
            "email": "",
            "desc": f"{desc}",
            "date": f"{today}",
            "city": "",
            "state": "",
            "address": "",
            "postal_code": "",
            "country_code": "",
            "order_id": "",
            "status": "",
            "mail_sent": "False",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


def PublicTransactionUpdate(
    payment_id,
    amount,
    currency,
    name,
    email,
    city,
    state,
    address,
    postal_code,
    country_code,
):
    headers = {
        "content-type": "application/json",
    }
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "PublicTransactions",
        "document": "PublicTransactions",
        "team_member_ID": "1221001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "payment_id": f"{payment_id}",
        },
        "update_field": {
            "amount": f"{amount}",
            "currency": f"{currency}",
            "name": f"{name}",
            "email": f"{email}",
            "city": f"{city}",
            "state": f"{state}",
            "address": f"{address}",
            "postal_code": f"{postal_code}",
            "country_code": f"{country_code}",
            "order_id": f"{payment_id}",
            "status": "succeeded",
            "mail_sent": "True",
        },
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


def GetPublicTransaction(payment_id):
    headers = {
        "content-type": "application/json",
    }
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "PublicTransactions",
        "document": "PublicTransactions",
        "team_member_ID": "1221001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": {
            "payment_id": f"{payment_id}",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)
    return json_data
