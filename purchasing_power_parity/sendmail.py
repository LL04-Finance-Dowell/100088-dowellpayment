import os
import requests
from django.template.loader import render_to_string
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()



def send_mail(
    email,
    base_price_in_country,
    calculated_price_in_target_country,
    price_in_base_country,
    basecountry,
    targetcountry,
    target_price,
    calculated_price_base_on_ppp,
):
    # API endpoint to send the email

    url = "https://100085.pythonanywhere.com/api/email/"

    EMAIL_FROM_WEBSITE = """
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Samanta Content Evaluator</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica,Arial,sans-serif;min-width:100px;overflow:auto;line-height:2">
                                <div style="margin:50px auto;width:70%;padding:20px 0">
                                <div style="border-bottom:1px solid #eee">
                                    <a href="#" style="font-size:1.2em;color: #00466a;text-decoration:none;font-weight:600">Dowell UX Living Lab</a>
                                </div>
                                <p style="font-size:1.1em"> {email} make use of Purcharsing Power Parity Application</p>
                                <p style="font-size:1.1em">Base Country : {base_country}</p>
                                <p style="font-size:1.1em">Target Country : {target_country}</p>
                                <p style="font-size:1.1em">Price In Base Country : {price_in_base_country}</p>
                                <p style="font-size:1.1em">Base Price In {base_country} : {base_price_in_country},</p>
                                <p style="font-size:1.1em">Calculated Price In {target_country} : {calculated_price_in_target_country}</p>
                                <p style="font-size:1.1em">Target Price : {target_price}</p>
                                <p style="font-size:1.1em">Calculated Price Based On PPP : {calculated_price_base_on_ppp}</p>
                                </div>
                            </div>
                        </body>
                        </html>
                      """
    email_content = EMAIL_FROM_WEBSITE.format(
        email=email,
        base_country=basecountry,
        base_price_in_country=base_price_in_country,
        target_country=targetcountry,
        calculated_price_in_target_country=calculated_price_in_target_country,
        price_in_base_country=price_in_base_country,
        target_price=target_price,
        calculated_price_base_on_ppp=calculated_price_base_on_ppp,
    )

    payload = {
        "toname": "sodiq",
        "toemail": "sodiqb86@gmail.com",
        "subject": "Purchasing Power Parity",
        "email_content": email_content,
    }
    response = requests.post(url, json=payload)
    print(response.text)
    return response.text
