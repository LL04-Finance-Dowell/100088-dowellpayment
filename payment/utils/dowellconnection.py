import requests
import json


# COLLECTIONS FOR DOWELL INTERNAL TEAM
"""ADD PAYMENT DETAILS TO DATABASE"""


def CreateDowellTransaction(
    payment_id, session_id, desc, today, template_id=None, voucher_code=None
):
    headers = {
        "content-type": "application/json",
    }

    # API endpoint to connect to dowellconnection
    url = "http://uxlivinglab.pythonanywhere.com/"
    
    ref_number = 0
    #get count
    get_count_data =  {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "DowellTransactions",
        "document": "DowellTransactions",
        "team_member_ID": "1220001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": {
            "count": "count",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    get_count_resp = json.loads(requests.post(url, json=get_count_data, headers=headers).json())
    print("count data",get_count_resp)

    #Create a count table if its not created and set the value to 1
    if get_count_resp["data"] == None:
        print("yes")
        create_count_data =  {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "DowellTransactions",
        "document": "DowellTransactions",
        "team_member_ID": "1220001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "count": "count",
            "value": 1
        },
        "update_field": {},
        "platform": "bangalore",
    }
        create_count_resp = json.loads(requests.post(url, json=create_count_data, headers=headers).json())
        ref_number = 1
        print("create_count_data",create_count_resp)
    
    #increament the count
    if get_count_resp["data"] != None:
        value = get_count_resp["data"]["value"]
        print("value",value)
        new_value = value+1
        print("new_value",new_value)
        data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "DowellTransactions",
        "document": "DowellTransactions",
        "team_member_ID": "1220001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "count": "count",
        },
        "update_field": {
            "value": new_value
        },
        "platform": "bangalore",
    }
        update_count_resp = json.loads(requests.post(url, json=data, headers=headers).json())
        ref_number = new_value
        print("update_count_resp",update_count_resp)


    date = f"{today}".split("-")[0]
    invoice_number = f"DI{date}{ref_number}"
    order_number = f"DO{date}{ref_number}"
    

    # print("today",today)
    voucher = voucher_code if voucher_code is not None else ""
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
            "voucher_code": f"{voucher}",
            "ref_id": "",
            "invoice_number":invoice_number,
            "order_number":order_number,
            "status": "",
            "mail_sent": "False",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    print("dowellTrans")
    print(response)
    json_data = json.loads(response.json())
    print(json_data)
    return json_data


"""UPDATE PAYMENT DETAILS IN DATABASE"""


def UpdateDowellTransaction(
    payment_id,
    ref_id,
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

    # API endpoint to connect to dowellconnection
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
            "ref_id": f"{ref_id}",
            "status": "succeeded",
            "mail_sent": "True",
        },
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


"""GET PAYMENT DETAILS FROM DATABASE"""


def GetDowellTransaction(payment_id):
    headers = {
        "content-type": "application/json",
    }

    # API endpoint to connect to dowellconnection
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


# COLLECTIONS FOR WORKFLOW AI INTERNAL TEAM
"""ADD PAYMENT DETAILS TO DATABASE"""


def CreateWorkflowPublicTransaction(
    payment_id, session_id, desc, today, template_id=None, voucher_code=None
):
    headers = {
        "content-type": "application/json",
    }

    # API endpoint to connect to dowellconnection
    url = "http://uxlivinglab.pythonanywhere.com/"

    ref_number = 0
    #get count
    get_count_data =  {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WorkflowTransactions",
        "document": "WorkflowTransactions",
        "team_member_ID": "1225001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": {
            "count": "count",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    get_count_resp = json.loads(requests.post(url, json=get_count_data, headers=headers).json())
    print("count data",get_count_resp)

    #Create a count table if its not created and set the value to 1
    if get_count_resp["data"] == None:
        print("yes")
        create_count_data =  {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WorkflowTransactions",
        "document": "WorkflowTransactions",
        "team_member_ID": "1225001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "count": "count",
            "value": 1
        },
        "update_field": {},
        "platform": "bangalore",
    }
        create_count_resp = json.loads(requests.post(url, json=create_count_data, headers=headers).json())
        ref_number = 1
        print("create_count_data",create_count_resp)
    
    #increament the count
    if get_count_resp["data"] != None:
        value = get_count_resp["data"]["value"]
        print("value",value)
        new_value = value+1
        print("new_value",new_value)
        data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WorkflowTransactions",
        "document": "WorkflowTransactions",
        "team_member_ID": "1225001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "count": "count",
        },
        "update_field": {
            "value": new_value
        },
        "platform": "bangalore",
    }
        update_count_resp = json.loads(requests.post(url, json=data, headers=headers).json())
        ref_number = new_value
        print("update_count_resp",update_count_resp)


    date = f"{today}".split("-")[0]
    invoice_number = f"DI{date}{ref_number}"
    order_number = f"DO{date}{ref_number}"
    

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WorkflowTransactions",
        "document": "WorkflowTransactions",
        "team_member_ID": "1225001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "payment_id": f"{payment_id}",
            "session_id": f"{session_id}",
            "template_id": f"{template_id}",
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
            "ref_id": "",
            "invoice_number":f"{invoice_number}",
            "order_number":f"{order_number}",
            "status": "",
            "mail_sent": "False",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


"""UPDATE PAYMENT DETAILS IN DATABASE"""


def UpdateWorkflowPublicTransaction(
    payment_id,
    ref_id,
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

    # API endpoint to connect to dowellconnection
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WorkflowTransactions",
        "document": "WorkflowTransactions",
        "team_member_ID": "1225001",
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
            "ref_id": f"{ref_id}",
            "status": "succeeded",
            "mail_sent": "True",
        },
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


"""GET PAYMENT DETAILS FROM DATABASE"""


def GetWorkflowPublicTransaction(payment_id):
    headers = {
        "content-type": "application/json",
    }

    # API endpoint to connect to dowellconnection
    url = "http://uxlivinglab.pythonanywhere.com/"

    data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "WorkflowTransactions",
        "document": "WorkflowTransactions",
        "team_member_ID": "1225001",
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


# COLLECTIONS FOR PUBLIC
"""ADD PAYMENT DETAILS TO DATABASE"""


def CreatePublicTransaction(
    payment_id, session_id, desc, today, template_id=None, voucher_code=None
):
    headers = {
        "content-type": "application/json",
    }

    # API endpoint to connect to dowellconnection
    url = "http://uxlivinglab.pythonanywhere.com/"

    ref_number = 0
    #get count
    get_count_data =  {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "PublicTransactions",
        "document": "PublicTransactions",
        "team_member_ID": "1221001",
        "function_ID": "ABCDE",
        "command": "find",
        "field": {
            "count": "count",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    get_count_resp = json.loads(requests.post(url, json=get_count_data, headers=headers).json())
    print("count data",get_count_resp)

    #Create a count table if its not created and set the value to 1
    if get_count_resp["data"] == None:
        print("yes")
        create_count_data =  {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "PublicTransactions",
        "document": "PublicTransactions",
        "team_member_ID": "1221001",
        "function_ID": "ABCDE",
        "command": "insert",
        "field": {
            "count": "count",
            "value": 1
        },
        "update_field": {},
        "platform": "bangalore",
    }
        create_count_resp = json.loads(requests.post(url, json=create_count_data, headers=headers).json())
        ref_number = 1
        print("create_count_data",create_count_resp)
    
    #increament the count
    if get_count_resp["data"] != None:
        value = get_count_resp["data"]["value"]
        print("value",value)
        new_value = value+1
        print("new_value",new_value)
        data = {
        "cluster": "dowellpayment",
        "database": "dowellpayment",
        "collection": "PublicTransactions",
        "document": "PublicTransactions",
        "team_member_ID": "1221001",
        "function_ID": "ABCDE",
        "command": "update",
        "field": {
            "count": "count",
        },
        "update_field": {
            "value": new_value
        },
        "platform": "bangalore",
    }
        update_count_resp = json.loads(requests.post(url, json=data, headers=headers).json())
        ref_number = new_value
        print("update_count_resp",update_count_resp)


    date = f"{today}".split("-")[0]
    invoice_number = f"DI{date}{ref_number}"
    order_number = f"DO{date}{ref_number}"
    

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
            "ref_id": "",
            "invoice_number":f"{invoice_number}",
            "order_number":f"{order_number}",
            "status": "",
            "mail_sent": "False",
        },
        "update_field": {},
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


"""UPDATE PAYMENT DETAILS IN DATABASE"""


def UpdatePublicTransaction(
    payment_id,
    ref_id,
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

    # API endpoint to connect to dowellconnection
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
            "ref_id": f"{ref_id}",
            "status": "succeeded",
            "mail_sent": "True",
        },
        "platform": "bangalore",
    }
    response = requests.post(url, json=data, headers=headers)
    json_data = json.loads(response.json())
    print(json_data)


"""GET PAYMENT DETAILS FROM DATABASE"""


def GetPublicTransaction(payment_id):
    headers = {
        "content-type": "application/json",
    }

    # API endpoint to connect to dowellconnection
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
