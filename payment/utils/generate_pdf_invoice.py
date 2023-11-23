import tempfile
import os
from django.conf import settings
from django.http import HttpResponse
from weasyprint import HTML


# name,address,country,invoice_number,invoice_date,order_number,payment_method
def generate_invoice(
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
):
    email_content = f"""
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      /* Global styles */
      body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        margin-top: 150px;
        margin-left:0px
        width: 100%;
        background-color: white;
      }}
      .container {{
        height: 100vh;
        width: 100%;
        margin: 0 auto;
        background-color: white;
        padding: 20px;
        border: 2px solid #000000;
        border-radius: 10px;
      }}
      h1 {{
        font-size: 24px;
        font-weight: bold;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 100px;
      }}
      table,
      th,
      td {{
        border: 2px solid #000; /* Border lines are bold */
      }}
      th,
      td {{
        padding: 10px;
        text-align: left;
        font-weight: bold; /* Make table content bold */
      }}
      .company-details {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
      }}
      .company-details-text-container {{
        display: block;
      }}
      .invoice-details {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 20px;
      }}

      .table-bold {{
        border: 2px solid #000;
        font-weight: bold;
        background-color: black;
        color: white;
      }}
      .width {{
        width: 70%;
      }}

      @media (max-width: 768px) {{
        .container {{
          width: 100%;
        }}
        .tableContainer {{
          overflow-x: auto;
        }}
        /* .invoice-details {{
          flex-direction: column;
        }} */
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="company-details">
        <div>
          <img
            src="https://100088.pythonanywhere.com/static/images/Logo_.png"
            alt="Company Logo"
            style="max-width: 100px; display: block"
          />
        </div>
        <div class="company-details-text-container">
          <p>DOWELL RESEARCH PTE. LTD</p>
          <p>#42-00 6 BATTERY ROAD</p>
          <p>Singapore, 049909, SINGAPORE</p>
        </div>
      </div>
      <h1 style="margin-top: 40px; margin-bottom: 10px">Invoice</h1>
      <div class="invoice-details">
        <div style="width: 45%">
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
                  <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Name :</strong>
        <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
          {name}
        </span>
          </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Address :</strong>
          <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
            {address}
          </span>
          </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">City :</strong>
        <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
          {city}
        </span>
          </div>
        </div>
        <div style="width: 50%;padding-left:150px">
        <div style="display: flex; flex-wrap: wrap; margin-bottom: 10px">
          <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Invoice Number :</strong>
          <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
            {invoice_number}
          </span>
        </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px"
              >Invoice Date :
            </strong>
            <span
              style="
                word-wrap: break-word;
                text-overflow: ellipsis;
                overflow: hidden;
              "
            >
              {date}</span
            >
          </div>
          <div style="display: flex; flex-wrap: wrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Order Number :</strong>
            <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
              {order_number}
            </span>
          </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px"
              >Payment Method :
            </strong>
            <span
              style="
                word-wrap: break-word;
                text-overflow: ellipsis;
                overflow: hidden;
              "
            >
              {payment_method}</span
            >
          </div>
        </div>
      </div>
      <div class="tableContainer">
        <table>
          <tbody>
            <tr>
              <th class="table-bold width">Product</th>
              <th class="table-bold">Quantity</th>
              <th class="table-bold">Price</th>
            </tr>
            <tr>
              <td>{desc}</td>
              <td>1</td>
              <td>{amount}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p style="text-align: right; margin-right: 20px">
        Sub Total {currency} {amount}
      </p>
      <div style="width: 100%; background-color: grey; height: 1px"></div>
      <p style="text-align: right; margin-right: 20px; font-weight: 800">
        Total {currency} {amount}
      </p>
    </div>
  </body>
</html>
                """

    pdf_data = HTML(string=email_content).write_pdf()
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf", dir=settings.MEDIA_ROOT
    ) as temp_file:
        temp_file.write(pdf_data)
        print(f"Temporary PDF file saved at: {temp_file.name}")
    pdf_filename = os.path.basename(temp_file.name)
    pdf_url = f"http://127.0.0.1:8000/api/pdf/{pdf_filename}"
    print(pdf_filename)
    print(pdf_url)
    return pdf_url


def generate_invoice_with_voucher(
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
):
    email_content = f"""

                <html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      /* Global styles */
      body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        margin-top: 150px;
        margin-left:0px
        width: 100%;
        background-color: white;
      }}
      .container {{
        height: 100vh;
        width: 100%;
        margin: 0 auto;
        background-color: white;
        padding: 20px;
        border: 2px solid #000000;
        border-radius: 10px;
      }}
      h1 {{
        font-size: 24px;
        font-weight: bold;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 100px;
      }}
      table,
      th,
      td {{
        border: 2px solid #000; /* Border lines are bold */
      }}
      th,
      td {{
        padding: 10px;
        text-align: left;
        font-weight: bold; /* Make table content bold */
      }}
      .company-details {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
      }}
      .company-details-text-container {{
        display: block;
      }}
      .invoice-details {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 20px;
      }}

      .table-bold {{
        border: 2px solid #000;
        font-weight: bold;
        background-color: black;
        color: white;
      }}
      .width {{
        width: 70%;
      }}

      @media (max-width: 768px) {{
        .container {{
          width: 100%;
        }}
        .tableContainer {{
          overflow-x: auto;
        }}
        /* .invoice-details {{
          flex-direction: column;
        }} */
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="company-details">
        <div>
          <img
            src="https://100088.pythonanywhere.com/static/images/Logo_.png"
            alt="Company Logo"
            style="max-width: 100px; display: block"
          />
        </div>
        <div class="company-details-text-container">
          <p>DOWELL RESEARCH PTE. LTD</p>
          <p>#42-00 6 BATTERY ROAD</p>
          <p>Singapore, 049909, SINGAPORE</p>
        </div>
      </div>
      <h1 style="margin-top: 40px; margin-bottom: 10px">Invoice</h1>
      <div class="invoice-details">
        <div style="width: 45%">
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Name :</strong>
          <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
            {name}
          </span>
          </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Address :</strong>
          <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
            {address}
          </span>
          </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">City :</strong>
          <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
            {city}
          </span>
          </div>
        </div>
        <div style="width: 50%;padding-left:150px">
        <div style="display: flex; flex-wrap: wrap; margin-bottom: 10px">
        <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Invoice Number :</strong>
        <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
          {invoice_number}
        </span>
      </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px"
              >Invoice Date :
            </strong>
            <span
              style="
                word-wrap: break-word;
                text-overflow: ellipsis;
                overflow: hidden;
              "
            >
              {date}</span
            >
          </div>
          <div style="display: flex; flex-wrap: wrap; margin-bottom: 10px">
          <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Order Number :</strong>
          <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
            {order_number}
          </span>
        </div>
          <div style="display: flex; flex-wrap: nowrap; margin-bottom: 10px">
            <strong style="white-space: nowrap; margin-right: 10px"
              >Payment Method :
            </strong>
            <span
              style="
                word-wrap: break-word;
                text-overflow: ellipsis;
                overflow: hidden;
              "
            >
              {payment_method}</span
            >
          </div>
                <div style="display: flex; flex-wrap: wrap; margin-bottom: 10px">
        <strong style="white-space: nowrap; margin-right: 10px; flex-basis: 120px;">Voucher Code :</strong>
        <span style="word-wrap: break-word; word-break: break-all; overflow: hidden;">
          {voucher_code}
        </span>
      </div>
        </div>
      </div>
      <div class="tableContainer">
        <table>
          <tbody>
            <tr>
              <th class="table-bold width">Product</th>
              <th class="table-bold">Quantity</th>
              <th class="table-bold">Price</th>
            </tr>
            <tr>
              <td>{desc}</td>
              <td>1</td>
              <td>{amount}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p style="text-align: right; margin-right: 20px">
        Sub Total {currency} {amount}
      </p>
      <div style="width: 100%; background-color: grey; height: 1px"></div>
      <p style="text-align: right; margin-right: 20px; font-weight: 800">
        Total {currency} {amount}
      </p>
    </div>
  </body>
</html>
"""
    pdf_data = HTML(string=email_content).write_pdf()
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf", dir=settings.MEDIA_ROOT
    ) as temp_file:
        temp_file.write(pdf_data)
        print(f"Temporary PDF file saved at: {temp_file.name}")
    pdf_filename = os.path.basename(temp_file.name)
    pdf_url = f"http://127.0.0.1:8000/api/pdf/{pdf_filename}"
    print(pdf_filename)
    print(pdf_url)
    return pdf_url