import base64
from io import BytesIO

import pyotp
import qrcode


ISSUER_NAME = "StayLink"


def generate_mfa_secret():
    return pyotp.random_base32()


def get_totp(secret):
    return pyotp.TOTP(secret)


def generate_mfa_uri(user, secret):
    totp = get_totp(secret)

    return totp.provisioning_uri(
        name=user.email,
        issuer_name=ISSUER_NAME
    )


def generate_qr_code_base64(uri):
    qr = qrcode.make(uri)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:image/png;base64,{qr_base64}"


def verify_mfa_code(secret, code):
    if not secret or not code:
        return False

    totp = get_totp(secret)

    return totp.verify(
        code,
        valid_window=1
    )