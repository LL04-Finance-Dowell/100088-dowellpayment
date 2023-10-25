import os
import requests
from django.template.loader import render_to_string
from io import BytesIO
from datetime import date,datetime
from dotenv import load_dotenv

load_dotenv()

mail_id = os.getenv("MAIL_ID", None)


def send_mail(
    email,
    base_currency,
    target_currency,
    base_price_in_country,
    calculated_price_in_target_country,
    price_in_base_country,
    basecountry,
    targetcountry,
    exchange_rate,
    target_price,
    calculated_price_base_on_ppp,
):
    # API endpoint to send the email

    url = "https://100085.pythonanywhere.com/api/email/"

    EMAIL_FROM_WEBSITE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DoWell World Price Indicator</title>
  </head>
  <body
    style="
      font-family: Arial, sans-serif;
      background-color: #ffffff;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
    "
  >
    <div style="width: 100%; background-color: #ffffff;">
      <header
        style="
          color: #fff;
          display: flex;
          text-align: center;
          justify-content: center;
          padding: 5px;
        "
      >
        <img
          src="https://dowellfileuploader.uxlivinglab.online/hr/logo-2-min-min.png"
          height="140px"
          width="140px"
         style="display: block; margin: 0 auto;"
        />
      </header>
      <article style="margin-top: 20px; text-align: center;">
        <h2>DoWell World Price Indicator</h2>
      </article>

      <main style="padding: 20px;">
        <section style="margin: 20px;">
          <p>From {email},</p>
          <p>Result from DoWell World Price Indicator :</p>
          <p style="text-align: left;">
            <span style="font-weight: bold; font-size: 1.2rem;"
              >Base Price in {base_country} : {base_price_in_country}</span
            >
          </p>
          <p style="text-align: left;">
            <span style="font-weight: bold; font-size: 1.2rem;"
              >Calculated Price in {target_country} : {calculated_price_in_target_country}</span
            >
          </p>
          <p style="font-weight: bold; font-size: 14px;">Detailed information :</p>
          <ul style="font-size: 14px;">
            <li>Base Currency : {base_currency}</li>
            <li>Base Country : {base_country}</li>
            <li>Target Country : {target_country}</li>
            <li>Target Price : {target_price}</li>
            <li>Price In Base Country : {price_in_base_country}</li>
            <li>Base Price In {base_country} : {base_price_in_country}</li>
            <li>Calculated Price In {target_country} : {calculated_price_in_target_country}</li>
            <li>Calculated Price Based On PPP : {calculated_price_base_on_ppp}</li>
            <li>Exchange rate. 1 {base_currency} = {exchange_rate:.4f} {target_currency} </li>
          </ul>
          <div style="margin: 20px;">
            <p>DoWell UX Living Lab Team</p>
          </div>
        </section>
      </main>

      <footer
        style="
          background-color: #005733;
          color: #fff;
          text-align: center;
          padding: 10px;
        "
      >
        <a
          href="https://www.uxlivinglab.org/"
          style="
            text-align: center;
            color: white;
            margin-bottom: 20px;
            padding-bottom: 10px;
          "
          >DoWell UX Living Lab</a
        >
        <p style="margin-top: 10px; font-size: 13px;">
          &copy; 2023-All rights reserved.
        </p>
      </footer>
    </div>
  </body>
</html>
"""
    email_content = EMAIL_FROM_WEBSITE.format(
        email=email,
        base_currency=base_currency,
        target_currency=target_currency,
        base_country=basecountry,
        base_price_in_country=base_price_in_country,
        target_country=targetcountry,
        calculated_price_in_target_country=calculated_price_in_target_country,
        price_in_base_country=price_in_base_country,
        exchange_rate=exchange_rate,
        target_price=target_price,
        calculated_price_base_on_ppp=calculated_price_base_on_ppp,
    )


    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    payload = {
        "toname": "sodiq",
        "toemail": f"{mail_id}",
        "subject": f"{email} result for purchasing power parity {date_time}",
        "email_content": email_content,
    }
    response = requests.post(url, json=payload)
    print(response.text)
    return response.text