import requests


#deposit email
def send_transaction_email(user_name, user_email, amount):
        # API endpoint to send the email
        url = f"https://100085.pythonanywhere.com/api/email/"
        name = user_name
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
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {name},</p>
                                <p style="font-size: 1.1em; text-align: center;">Your deposit was successful.</p>
                                <p style="font-size: 1.1em; text-align: center;">You have added an amount of ${amount} to your wallet.</p>
                                <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
                            </div>
                        </body>
                        </html>
                        """

        email_content = EMAIL_FROM_WEBSITE.format(name=name, amount=amount)
        payload = {
            "toname": name,
            "toemail": user_email,
            "subject": "Walllet Deposit",
            "email_content": email_content,
        }
        response = requests.post(url, json=payload)
        print(response.text)
        return response.text

#passwordresetemail

def send_password_reset_email(username,email, otp_key):
        # API endpoint to send the email
        url = f"https://100085.pythonanywhere.com/api/email/"
        print(username)
        print(email)
        EMAIL_FROM_WEBSITE = """
                <!DOCTYPE html>
<html
  lang="en"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title></title>
    <!--[if mso]>
      <noscript>
        <xml>
          <o:OfficeDocumentSettings>
            <o:PixelsPerInch>96</o:PixelsPerInch>
          </o:OfficeDocumentSettings>
        </xml>
      </noscript>
    <![endif]-->
    <style>
      table,
      td,
      div,
      h1,
      p {
        font-family: Arial, sans-serif;
      }
      td {
        padding-left: 20px;
      }
      .table-bold {
        border: 2px solid #000;
        font-weight: bold;
        background-color: black;
        color: white;
      }
      .tableContainer {
        overflow-x: auto;
      }
    </style>
  </head>
  <body style="margin: 20px; padding: 0">
    <table
      role="presentation"
      style="
        width: 100%;
        border-collapse: collapse;
        border: 0;
        border-spacing: 0;
        background: #ffffff;
      "
    >
      <tr>
        <td align="center" style="padding: 0">
          <table style="border: 2px solid; width: 900px; border-radius: 15px">
            <tr>
              <td align="center">
                <table
                  style="
                    width: 750px;
                    border-collapse: collapse;
                    border-spacing: 0;
                    text-align: left;
                  "
                >
                  <tr>
                    <!-- header -->
                    <td >
                      <img
                        src="https://100088.pythonanywhere.com/static/images/Logo_.png"
                        alt=""
                        width="100"
                        style="height: auto; display: block"
                      />
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-left: 10">
                      <h2>
                        Dear {name},
                      </h2>
                      <h4>
                       You have requested for password reset
                      </h4>
                      <h4>
                        You OTP is : <span style="color: #2f9e44;">{otp_key}</span>
                       </h4>
                       <h5 style="color: red;">
                        if you didn't request password reset you can ignore this email 
                       </h5>
                    </td>
                  </tr>
                </table>
                <!-- <div class="tableContainer"> -->
                <!-- </div> -->
              
        </td>
      </tr>
    </table>
  </body>
</html>
            """
        email_content = EMAIL_FROM_WEBSITE.format(name=username, otp_key=otp_key)
        payload = {
            "toname": username,
            "toemail": email,
            "subject": "Password Reset",
            "email_content": email_content,
        }
        response = requests.post(url, json=payload)
        print(response.json())
        return response.text

#resendotp
def send_otp_email(username,email, otp_key):
        # API endpoint to send the email
        url = f"https://100085.pythonanywhere.com/api/email/"
        EMAIL_FROM_WEBSITE = """
                   <!DOCTYPE html>
<html
  lang="en"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title></title>
    <!--[if mso]>
      <noscript>
        <xml>
          <o:OfficeDocumentSettings>
            <o:PixelsPerInch>96</o:PixelsPerInch>
          </o:OfficeDocumentSettings>
        </xml>
      </noscript>
    <![endif]-->
    <style>
      table,
      td,
      div,
      h1,
      p {
        font-family: Arial, sans-serif;
      }
      td {
        padding-left: 20px;
      }
      .table-bold {
        border: 2px solid #000;
        font-weight: bold;
        background-color: black;
        color: white;
      }
      .tableContainer {
        overflow-x: auto;
      }
    </style>
  </head>
  <body style="margin: 20px; padding: 0">
    <table
      role="presentation"
      style="
        width: 100%;
        border-collapse: collapse;
        border: 0;
        border-spacing: 0;
        background: #ffffff;
      "
    >
      <tr>
        <td align="center" style="padding: 0">
          <table style="border: 2px solid; width: 900px; border-radius: 15px">
            <tr>
              <td align="center">
                <table
                  style="
                    width: 750px;
                    border-collapse: collapse;
                    border-spacing: 0;
                    text-align: left;
                  "
                >
                  <tr>
                    <!-- header -->
                    <td >
                      <img
                        src="https://100088.pythonanywhere.com/static/images/Logo_.png"
                        alt=""
                        width="100"
                        style="height: auto; display: block"
                      />
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-left: 10">
                      <h2>
                        Dear {name},
                      </h2>
                      <h4>
                       You have requested for password reset
                      </h4>
                      <h4>
                        You OTP is : <span style="color: #2f9e44;">{totp}</span>
                       </h4>
                       <h5 style="color: red;">
                        if you didn't request password reset you can ignore this email 
                       </h5>
                    </td>
                  </tr>
                </table>
                <!-- <div class="tableContainer"> -->
                <!-- </div> -->
              
        </td>
      </tr>
    </table>
  </body>
</html>

                    """

        email_content = EMAIL_FROM_WEBSITE.format(name=username, totp=otp_key)
        payload = {
            "toname": username,
            "toemail": email,
            "subject": "OTP Verification",
            "email_content": email_content,
        }
        response = requests.post(url, json=payload)
        print(response.text)
        return response.text