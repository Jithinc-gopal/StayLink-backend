from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth import get_user_model


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import (
    urlsafe_base64_encode
)

token_generator = PasswordResetTokenGenerator()


def send_verification_code_email(
    user,
    code
):

    subject = "Verify Your StayLink Account"

    from_email = settings.EMAIL_HOST_USER

    to = [user.email]

    text_content = (
        f"Your verification code is: {code}"
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial;">

        <div style="
            max-width:600px;
            margin:auto;
            padding:40px;
            background:#ffffff;
            border-radius:12px;
        ">

            <h1 style="color:#003d9b;">
                StayLink Email Verification
            </h1>

            <p>
                Hi <b>{user.first_name}</b>,
            </p>

            <p>
                Use the verification code below
                to activate your account.
            </p>

            <div style="
                font-size:36px;
                font-weight:bold;
                letter-spacing:8px;
                color:#003d9b;
                margin:30px 0;
            ">
                {code}
            </div>

            <p>
                This code will expire in 5 minutes.
            </p>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    msg.send()


def send_registration_email(user):
    subject = "Welcome to StayLink 🎉"
    from_email = settings.EMAIL_HOST_USER
    to = [user.email]
    print(user.first_name)

    text_content = f"Hi {user.first_name}, your account is created."

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background-color: #f4f6fb;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            }}
            .header {{
                background: linear-gradient(135deg, #003d9b, #0052cc);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
                color: #333;
                line-height: 1.6;
            }}
            .content h2 {{
                margin-top: 0;
                color: #003d9b;
            }}
            .button {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: #003d9b;
                color: #ffffff;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                padding: 20px;
                background: #f9f9ff;
            }}
        </style>
    </head>
    <body>

        <div class="container">

            <div class="header">
                <h1>StayLink</h1>
                <p>Seamless Stays, Curated for You</p>
            </div>

            <div class="content">
                <h2>Welcome to StayLink 🎉</h2>
                <p>Hi <b>{user.first_name}</b>,</p>

                <p>
                    Your account has been successfully created. 
                    You're now ready to explore properties, connect with brokers, 
                    and experience a smarter way to stay.
                </p>

                <p>
                    Start your journey with StayLink and discover premium listings tailored just for you.
                </p>

                <a href="#" class="button">Explore Now</a>
            </div>

            <div class="footer">
                © 2024 StayLink • All rights reserved
            </div>

        </div>

    </body>
    </html>
    """


    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
       
def send_owner_profile_pending_email(user):

    subject = "Profile Submitted Successfully ✅"

    from_email = settings.EMAIL_HOST_USER

    to = [user.email]

    text_content = (
        f"Hi {user.first_name}, "
        "your owner profile was submitted successfully "
        "and is waiting for admin approval."
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6fb; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:linear-gradient(135deg,#003d9b,#0052cc);
                color:white;
                padding:30px;
                text-align:center;
            ">

                <h1>StayLink</h1>

            </div>

            <div style="padding:30px;">

                <h2 style="color:#003d9b;">
                    Profile Submitted 🎉
                </h2>

                <p>
                    Hi <b>{user.first_name}</b>,
                </p>

                <p>
                    Your owner profile has been submitted successfully.
                </p>

                <p>
                    Our admin team will review your profile shortly.
                    Once approved, you can start listing properties.
                </p>

                <p>
                    Verification Status:
                    <b style="color:#eab308;">
                        Pending Approval
                    </b>
                </p>

            </div>

            <div style="
                text-align:center;
                padding:20px;
                font-size:12px;
                color:#777;
                background:#f9f9ff;
            ">
                © 2026 StayLink
            </div>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )
    msg.send()


def send_broker_profile_pending_email(user):

    subject = "Broker Profile Submitted Successfully ✅"

    from_email = settings.EMAIL_HOST_USER

    to = [user.email]

    text_content = (
        f"Hi {user.first_name}, "
        "your broker profile was submitted successfully "
        "and is waiting for admin approval."
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6fb; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:linear-gradient(135deg,#003d9b,#0052cc);
                color:white;
                padding:30px;
                text-align:center;
            ">

                <h1>StayLink</h1>

            </div>

            <div style="padding:30px;">

                <h2 style="color:#003d9b;">
                    Broker Profile Submitted 🎉
                </h2>

                <p>
                    Hi <b>{user.first_name}</b>,
                </p>

                <p>
                    Your broker profile has been submitted successfully.
                </p>

                <p>
                    Our admin team will review your broker account shortly.
                </p>

                <p>
                    Verification Status:
                    <b style="color:#eab308;">
                        Pending Approval
                    </b>
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    msg.send()


def send_admin_broker_notification(user):

    User = get_user_model()

    admins = User.objects.filter(
        role='admin'
    )

    admin_emails = [
        admin.email
        for admin in admins
    ]

    if not admin_emails:
        return

    subject = "New Broker Registration"

    from_email = settings.EMAIL_HOST_USER

    text_content = (
        f"{user.first_name} submitted "
        "a broker profile."
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6fb; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:linear-gradient(135deg,#003d9b,#0052cc);
                color:white;
                padding:30px;
                text-align:center;
            ">

                <h1>StayLink Admin</h1>

            </div>

            <div style="padding:30px;">

                <h2 style="color:#003d9b;">
                    New Broker Profile Submitted
                </h2>

                <p>
                    A new broker profile was submitted.
                </p>

                <ul>
                    <li>
                        <b>Name:</b>
                        {user.first_name}
                    </li>

                    <li>
                        <b>Email:</b>
                        {user.email}
                    </li>
                </ul>

                <p>
                    Please review and approve the broker profile.
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        admin_emails
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    msg.send()    

  
def send_admin_owner_notification(user):

    User = get_user_model()

    admins = User.objects.filter(
        role='admin'
    )

    admin_emails = [
        admin.email
        for admin in admins
    ]

    if not admin_emails:
        return

    subject = "New Owner Registration"

    from_email = settings.EMAIL_HOST_USER

    text_content = (
        f"{user.first_name} submitted "
        "a new owner profile."
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6fb; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:linear-gradient(135deg,#003d9b,#0052cc);
                color:white;
                padding:30px;
                text-align:center;
            ">

                <h1>StayLink Admin</h1>

            </div>

            <div style="padding:30px;">

                <h2 style="color:#003d9b;">
                    New Owner Profile Submitted
                </h2>

                <p>
                    A new owner profile was submitted.
                </p>

                <ul>
                    <li>
                        <b>Name:</b>
                        {user.first_name}
                    </li>

                    <li>
                        <b>Email:</b>
                        {user.email}
                    </li>
                </ul>

                <p>
                    Please review and approve the profile.
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        admin_emails
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    msg.send()


def send_profile_approved_email(user):

    subject = "Profile Approved ✅"

    from_email = settings.EMAIL_HOST_USER

    to = [user.email]

    text_content = (
        f"Hi {user.first_name}, "
        "your profile has been approved."
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6fb; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:linear-gradient(135deg,#16a34a,#22c55e);
                color:white;
                padding:30px;
                text-align:center;
            ">

                <h1>StayLink</h1>

            </div>

            <div style="padding:30px;">

                <h2 style="color:#16a34a;">
                    Profile Approved 🎉
                </h2>

                <p>
                    Hi <b>{user.first_name}</b>,
                </p>

                <p>
                    Your profile has been approved successfully.
                </p>

                <p>
                    You can now access all partner features
                    and start listing properties.
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    msg.send()
    
    
    
def send_profile_rejected_email(
    user,
    reason
):

    subject = "Profile Rejected ❌"

    from_email = settings.EMAIL_HOST_USER

    to = [user.email]

    text_content = (
        f"Hi {user.first_name}, "
        f"your profile was rejected.\n\n"
        f"Reason: {reason}"
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6fb; padding:20px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                background:linear-gradient(135deg,#dc2626,#ef4444);
                color:white;
                padding:30px;
                text-align:center;
            ">

                <h1>StayLink</h1>

            </div>

            <div style="padding:30px;">

                <h2 style="color:#dc2626;">
                    Profile Rejected
                </h2>

                <p>
                    Hi <b>{user.first_name}</b>,
                </p>

                <p>
                    Unfortunately your profile verification
                    was rejected by our admin team.
                </p>

                <p>
                    <b>Reason:</b>
                </p>

                <div style="
                    background:#fef2f2;
                    padding:15px;
                    border-radius:8px;
                    color:#991b1b;
                ">
                    {reason}
                </div>

                <p style="margin-top:20px;">
                    Please update your profile and try again.
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )

    msg.attach_alternative(
        html_content,
        "text/html"
    )

    msg.send()    
         