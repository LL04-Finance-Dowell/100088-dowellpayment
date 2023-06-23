import os
import requests
from django.template.loader import render_to_string
from dotenv import load_dotenv
load_dotenv()
mail_api_key = os.getenv("MAIL_API_KEY",None)



def send_mail(amount,currency,name,email,desc,date,city,address,postal_code,order_id,payment_method):
    order_template = 'payment/order.html'

    # API endpoint to send the email
    url = f"https://100085.pythonanywhere.com/api/v1/mail/{mail_api_key}/?type=send-email"
    
    amount = amount if amount else 0
    currency = currency if currency else ""
    name = name if name else ""
    email = email if email else ""
    desc = desc if desc else ""
    date = date if date else ""
    city = city if city else ""
    address = address if address else ""
    postal_code = postal_code if postal_code else ""
    Id = order_id if order_id else ""

    context = {
        "amount":amount,
        "currency":currency,
        "name":name,
        "email":email,
        "desc":desc,
        "date":date,
        "city":city, 
        "address":address,
        "postal_code":postal_code,
        "orderID":Id,
        "date": date,
        "payment_method":payment_method
    }
    
    # Email data
    email_data = {
        "email":email,
        "name":name,
        "fromName":"Dowell Research",
        "fromEmail" : "DowellResearch@gmail.com",
        "subject" : "Your Order Details",
        }

    html_body = render_to_string(order_template,context)
    email_data["body"] = html_body
    
    response = requests.post(url, data=email_data)
    response_json = response.json()
    return (response_json)