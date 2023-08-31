import os
import requests
from django.template.loader import render_to_string
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


def send_mail_one(
    amount,
    currency,
    name,
    email,
    desc,
    date,
    city,
    address,
    postal_code,
    ref_id,
    payment_method,
):
    order_template = "payment/order.html"

    # API endpoint to send the email
    url = f"https://100085.pythonanywhere.com/api/payment-status/"

    amount = amount if amount else 0
    currency = currency if currency else ""
    name = name if name else ""
    email = email if email else ""
    desc = desc if desc else ""
    date = date if date else ""
    city = city if city else ""
    address = address if address else ""
    postal_code = postal_code if postal_code else ""
    ref = ref_id if ref_id else ""

    context = {
        "amount": amount,
        "currency": currency,
        "name": name,
        "email": email,
        "desc": desc,
        "date": date,
        "city": city,
        "address": address,
        "postal_code": postal_code,
        "ref": ref,
        "date": date,
        "payment_method": payment_method,
    }

    # Email data
    email_data = {
        "toemail": email,
        "toname": name,
        "topic": "memberinvitation",
    }

    html_body = BytesIO(render_to_string(order_template, context).encode("utf-8"))
    files = {"file": html_body}

    response = requests.post(url, files=files, data=email_data)
    return response


def send_mail_two(
    amount,
    currency,
    name,
    email,
    desc,
    date,
    city,
    address,
    postal_code,
    voucher_code,
    ref_id,
    payment_method,
):
    order_template = "payment/order_two.html"

    # API endpoint to send the email
    url = f"https://100085.pythonanywhere.com/api/payment-status/"

    amount = amount if amount else 0
    currency = currency if currency else ""
    name = name if name else ""
    email = email if email else ""
    desc = desc if desc else ""
    date = date if date else ""
    city = city if city else ""
    address = address if address else ""
    postal_code = postal_code if postal_code else ""
    voucher_code = voucher_code if voucher_code else ""
    ref = ref_id if ref_id else ""

    context = {
        "amount": amount,
        "currency": currency,
        "name": name,
        "email": email,
        "desc": desc,
        "date": date,
        "city": city,
        "address": address,
        "postal_code": postal_code,
        "voucher_code": voucher_code,
        "ref": ref,
        "date": date,
        "payment_method": payment_method,
    }

    # Email data
    email_data = {
        "toemail": email,
        "toname": name,
        "topic": "memberinvitation",
    }

    html_body = BytesIO(render_to_string(order_template, context).encode("utf-8"))
    files = {"file": html_body}

    response = requests.post(url, files=files, data=email_data)
    return response
