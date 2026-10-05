import os
from pydantic import EmailStr
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv()  # Load environment variables from .env file

WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome</title>
</head>

<body style="margin:0; padding:0; background:#f4f4f4; font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
       style="padding:40px 0; background:#f4f4f4;">

    <tr>
        <td align="center">

            <table width="600" cellpadding="0" cellspacing="0"
                   style="background:#ffffff; max-width:600px;">

                <tr>
                    <td style="background:#2563eb; padding:30px; text-align:center;">
                        <h1 style="color:#ffffff; margin:0;">
                            Welcome!
                        </h1>
                    </td>
                </tr>

                <tr>
                    <td style="padding:40px;">

                        <h2 style="color:#222222;">
                            Welcome to our platform!
                        </h2>

                        <p style="color:#555555; font-size:16px; line-height:1.6;">
                            Your account has been successfully created.
                        </p>

                        <p style="color:#555555; font-size:16px; line-height:1.6;">
                            We're happy to have you with us.
                            You can now log in and start using our platform.
                        </p>

                        <p style="color:#555555; font-size:16px; line-height:1.6;">
                            Best regards,<br>
                            <strong>Our Team</strong>
                        </p>

                    </td>
                </tr>

                <tr>
                    <td style="background:#f8f8f8; padding:20px; text-align:center;">
                        <p style="margin:0; color:#999999; font-size:13px;">
                            © 2026 Our Company. All rights reserved.
                        </p>
                    </td>
                </tr>

            </table>

        </td>
    </tr>

</table>

</body>
</html>
"""

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_email(email_to: EmailStr):
    message = MessageSchema(
        subject='Welcome to Our Platform',
        recipients=[email_to],
        body=WELCOME_EMAIL_TEMPLATE,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

