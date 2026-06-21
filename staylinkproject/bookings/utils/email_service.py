from django.core.mail import EmailMultiAlternatives
from django.conf import settings



# ================================================================
# BOOKING EMAIL SERVICE
#
# Same pattern as accounts/utils/email_service.py
# Plain functions — called from tasks.py only
# Never call these directly from views
# ================================================================


def send_booking_confirmation_email(booking):
    """
    Sends booking confirmation email to traveler
    immediately after payment is verified.
    """

    traveler = booking.traveler
    property_obj = booking.property

    nights = (booking.check_out - booking.check_in).days
    remaining_amount = booking.total_amount - booking.advance_amount

    subject = f"Booking Confirmed — {property_obj.title} | StayLink"

    from_email = settings.EMAIL_HOST_USER

    to = [traveler.email]

    text_content = (
        f"Hi {traveler.first_name}, "
        f"your booking #{booking.id} at {property_obj.title} "
        f"is confirmed. Check-in: {booking.check_in}."
    )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f6fb;">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:#ffffff;
            border-radius:12px;
            overflow:hidden;
            box-shadow:0 10px 25px rgba(0,0,0,0.07);
        ">

            <!-- HEADER -->
            <div style="
                background:linear-gradient(135deg,#003d9b,#0052cc);
                color:white;
                padding:30px;
                text-align:center;
            ">
                <h1 style="margin:0;font-size:26px;letter-spacing:1px;">
                    StayLink
                </h1>
                <p style="margin:6px 0 0;opacity:0.85;font-size:14px;">
                    Seamless Stays, Curated for You
                </p>
            </div>

            <!-- BODY -->
            <div style="padding:36px;">

                <!-- BADGE -->
                <div style="
                    display:inline-block;
                    background:#d4edda;
                    color:#155724;
                    padding:6px 16px;
                    border-radius:20px;
                    font-size:13px;
                    font-weight:bold;
                    margin-bottom:20px;
                ">
                    ✓ Booking Confirmed
                </div>

                <h2 style="margin:0 0 8px;color:#111;font-size:22px;">
                    Your stay is booked, {traveler.first_name}!
                </h2>

                <p style="color:#555;line-height:1.7;margin-top:8px;">
                    Your payment was successful and your booking has been
                    confirmed. Here are your booking details:
                </p>

                <!-- BOOKING CARD -->
                <div style="
                    background:#f9f9f9;
                    border-radius:10px;
                    padding:24px;
                    margin:24px 0;
                ">
                    <table style="width:100%;border-collapse:collapse;">

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Property
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {property_obj.title}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Check-in
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {booking.check_in.strftime('%d %B %Y')}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Check-out
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {booking.check_out.strftime('%d %B %Y')}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Nights
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {nights}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Guests
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {booking.guests_count}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Advance Paid
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#16a34a;
                                text-align:right;
                                font-size:14px;
                            ">
                                ₹ {booking.advance_amount}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Total Amount
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                ₹ {booking.total_amount}
                            </td>
                        </tr>

                        <tr>
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Booking ID
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#003d9b;
                                text-align:right;
                                font-size:14px;
                            ">
                                #{booking.id}
                            </td>
                        </tr>

                    </table>
                </div>

                <p style="color:#555;line-height:1.7;">
                    The remaining amount of
                    <strong>₹ {remaining_amount}</strong>
                    is to be paid at the property during check-in.
                </p>

                <p style="color:#555;line-height:1.7;margin-top:20px;">
                    See you soon! 🏡<br>
                    <strong>The StayLink Team</strong>
                </p>

            </div>

            <!-- FOOTER -->
            <div style="
                text-align:center;
                padding:20px;
                font-size:12px;
                color:#aaa;
                background:#f9f9ff;
                border-top:1px solid #eee;
            ">
                © 2025 StayLink. All rights reserved.
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

    msg.attach_alternative(html_content, "text/html")

    msg.send()


def send_booking_reminder_email(booking, reminder_type):
    """
    Sends a reminder email to the traveler.

    reminder_type:
      'two_days'  → 2 days before check-in
      'two_hours' → 2 hours before check-in
    """

    traveler = booking.traveler
    property_obj = booking.property
    remaining_amount = booking.total_amount - booking.advance_amount
    
    if reminder_type == 'one_week':

        badge_text = '🗓️ 1 Week to Go'

        badge_color = '#dbeafe'

        badge_text_color = '#1e40af'

        heading = (
            f"Your trip is only one week away, "
            f"{traveler.first_name}!"
        )

        message = (
            f"Your stay at "
            f"<strong>{property_obj.title}</strong> "
            f"begins in one week on "
            f"<strong>{booking.check_in.strftime('%d %B %Y')}</strong>."
        )

        subject = (
            f"Reminder: Your Stay Begins in 1 Week | StayLink"
        )

    elif reminder_type == 'two_days':
        badge_text = '📅 2 Days to Go'
        badge_color = '#fff3cd'
        badge_text_color = '#856404'
        heading = f"Your check-in is in 2 days, {traveler.first_name}!"
        message = (
            f"Just a reminder that your stay at "
            f"<strong>{property_obj.title}</strong> "
            f"begins in 2 days on "
            f"<strong>{booking.check_in.strftime('%d %B %Y')}</strong>. "
            f"Please make sure you are prepared for your trip!"
        )
        subject = f"Reminder: Check-in in 2 days — {property_obj.title} | StayLink"

    elif reminder_type == 'two_hours':
        badge_text = '⏰ Check-in Today'
        badge_color = '#fde8e8'
        badge_text_color = '#9b1c1c'
        heading = f"Your check-in is in 2 hours, {traveler.first_name}!"
        message = (
            f"Your stay at <strong>{property_obj.title}</strong> begins today! "
            f"Check-in time is approaching. Please ensure you have "
            f"your Booking ID <strong>#{booking.id}</strong> "
            f"and a valid ID ready."
        )
        subject = f"Reminder: Check-in Today — {property_obj.title} | StayLink"

    else:
        return

    from_email = settings.EMAIL_HOST_USER
    to = [traveler.email]
    text_content = f"Hi {traveler.first_name}, {heading}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f6fb;">

        <div style="
            max-width:600px;
            margin:40px auto;
            background:#ffffff;
            border-radius:12px;
            overflow:hidden;
            box-shadow:0 10px 25px rgba(0,0,0,0.07);
        ">

            <!-- HEADER -->
            <div style="
                background:linear-gradient(135deg,#003d9b,#0052cc);
                color:white;
                padding:30px;
                text-align:center;
            ">
                <h1 style="margin:0;font-size:26px;letter-spacing:1px;">
                    StayLink
                </h1>
                <p style="margin:6px 0 0;opacity:0.85;font-size:14px;">
                    Seamless Stays, Curated for You
                </p>
            </div>

            <!-- BODY -->
            <div style="padding:36px;">

                <!-- BADGE -->
                <div style="
                    display:inline-block;
                    background:{badge_color};
                    color:{badge_text_color};
                    padding:6px 16px;
                    border-radius:20px;
                    font-size:13px;
                    font-weight:bold;
                    margin-bottom:20px;
                ">
                    {badge_text}
                </div>

                <h2 style="margin:0 0 8px;color:#111;font-size:22px;">
                    {heading}
                </h2>

                <p style="color:#555;line-height:1.7;margin-top:8px;">
                    {message}
                </p>

                <!-- BOOKING CARD -->
                <div style="
                    background:#f9f9f9;
                    border-radius:10px;
                    padding:24px;
                    margin:24px 0;
                ">
                    <table style="width:100%;border-collapse:collapse;">

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Property
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {property_obj.title}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Check-in
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {booking.check_in.strftime('%d %B %Y')}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Check-out
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {booking.check_out.strftime('%d %B %Y')}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Guests
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#111;
                                text-align:right;
                                font-size:14px;
                            ">
                                {booking.guests_count}
                            </td>
                        </tr>

                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Remaining at Check-in
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#dc2626;
                                text-align:right;
                                font-size:14px;
                            ">
                                ₹ {remaining_amount}
                            </td>
                        </tr>

                        <tr>
                            <td style="padding:10px 0;color:#888;font-size:14px;">
                                Booking ID
                            </td>
                            <td style="
                                padding:10px 0;
                                font-weight:bold;
                                color:#003d9b;
                                text-align:right;
                                font-size:14px;
                            ">
                                #{booking.id}
                            </td>
                        </tr>

                    </table>
                </div>

                <p style="color:#555;line-height:1.7;">
                    Please carry a valid photo ID for check-in.
                    The remaining amount is due at the property.
                </p>

                <p style="color:#555;line-height:1.7;margin-top:20px;">
                    Have a great stay! 🏡<br>
                    <strong>The StayLink Team</strong>
                </p>

            </div>

            <!-- FOOTER -->
            <div style="
                text-align:center;
                padding:20px;
                font-size:12px;
                color:#aaa;
                background:#f9f9ff;
                border-top:1px solid #eee;
            ">
                © 2025 StayLink. All rights reserved.
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

    msg.attach_alternative(html_content, "text/html")

    msg.send()
    
    



def send_review_request_email(booking):
    traveler = booking.traveler
    property_obj = booking.property

    review_link = (
        f"{settings.FRONTEND_URL}/traveler/bookings"
    )

    subject = f"How was your stay at {property_obj.title}?"

    from_email = settings.EMAIL_HOST_USER
    to = [traveler.email]

    text_content = (
        f"Hi {traveler.first_name or traveler.email},\n\n"
        f"Hope you enjoyed your stay at {property_obj.title}.\n"
        f"Please share your review here:\n{review_link}\n\n"
        f"Thank you,\nStayLink Team"
    )

    html_content = f"""
    <div style="font-family: Arial; line-height: 1.6;">
        <h2>How was your stay?</h2>

        <p>Hi {traveler.first_name or traveler.email},</p>

        <p>
            Hope you enjoyed your stay at
            <strong>{property_obj.title}</strong>.
        </p>

        <p>
            Your feedback helps future travelers choose better stays.
        </p>

        <a href="{review_link}"
           style="
             display:inline-block;
             padding:12px 20px;
             background:#0f172a;
             color:white;
             text-decoration:none;
             border-radius:10px;
             font-weight:bold;
           ">
            Write a Review
        </a>

        <p style="margin-top:20px;">
            Thank you,<br/>
            StayLink Team
        </p>
    </div>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to
    )

    email.attach_alternative(
        html_content,
        "text/html"
    )

    email.send()    