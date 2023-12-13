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
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Samanta Content Evaluator</title>
                </head>
                <body>
                    <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 2; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                        <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                        <p style="font-size: 1.1em; text-align: center;">Dear {name}, you have requested a password reset.</p>
                        <p style="font-size: 1.1em; text-align: center;">To reset your password, click the link below:</p>
                        <p style="font-size: 1.1em; text-align: center;">Your OTP is: {otp_key}</p>
                        <p style="font-size: 1.1em; text-align: center;">If you did not request this password reset, you can ignore this email.</p>

                    </div>
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
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Samanta Content Evaluator</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 2; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {name},</p>
                                <p style="font-size: 1.1em; text-align: center;">Your OTP for verification is: {totp}</p>
                                <p style="font-size: 1.1em; text-align: center;">If you did not request an OTP with us, you can ignore this email.</p>
                            </div>
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