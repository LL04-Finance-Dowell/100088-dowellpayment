from pyotp import TOTP
import secrets
import base64


def generate_totp_key():
        # Generate a random secret key as bytes
        secret_key_bytes = secrets.token_bytes(20)  # 20 bytes (160 bits)
        # Convert the bytes to a base32-encoded string
        secret_key = base64.b32encode(secret_key_bytes).decode("utf-8")
        # Create a TOTP instance
        totp = TOTP(
            secret_key, interval=30
        )  # Replace 'your-secret-key' with your secret key
        # Generate the TOTP token
        totp_key = totp.now()
        print(totp_key)
        return totp_key