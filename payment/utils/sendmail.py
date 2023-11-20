import os
import requests
from django.template.loader import render_to_string
from io import BytesIO
from dotenv import load_dotenv
from .generate_pdf_invoice import generate_invoice, generate_invoice_with_voucher

load_dotenv()

"""MAIL FUNCTION IF VOUCHER CODE IS NOT PROVIDED"""


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
    invoice_number,
    order_number,
    payment_method,
):
    pdf_url = generate_invoice(
        name, address, city, ref_id,invoice_number, order_number,date, payment_method, desc, amount, currency
    )
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
        "invoice_number":invoice_number,
        "order_number":order_number,
        "date": date,
        "payment_method": payment_method,
        "pdf_url": pdf_url,
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
    print("response mail", response)
    return response


"""MAIL FUNCTION IF VOUCHER CODE IS PROVIDED"""


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
    invoice_number,
    order_number,
    payment_method,
):
    order_template = "payment/order_two.html"

    pdf_url = generate_invoice_with_voucher(
        name,
        address,
        city,
        ref_id,
        invoice_number,
        order_number,
        date,
        payment_method,
        desc,
        amount,
        currency,
        voucher_code,
    )

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
        "invoice_number":invoice_number,
        "order_number":order_number,
        "date": date,
        "payment_method": payment_method,
        "pdf_url": pdf_url,
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
    print("response mail", response)
    return response
