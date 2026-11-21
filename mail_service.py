import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


def send_reset_email(recipient, reset_url):
    config = current_app.config

    username = config["MAIL_USERNAME"]
    password = config["MAIL_PASSWORD"]

    if (
        not username
        or not password
        or password == "DIEN_MAT_KHAU_UNG_DUNG_GOOGLE"
    ):
        raise RuntimeError(
            "Chua dien MAIL_USERNAME hoac MAIL_PASSWORD trong .env."
        )

    message = EmailMessage()
    message["Subject"] = "Mộc Hán - Đặt lại mật khẩu"
    message["From"] = username
    message["To"] = recipient

    message.set_content(
        "Xin chào,\n\n"
        "Mộc Hán nhận được yêu cầu đặt lại mật khẩu tài khoản của bạn.\n\n"
        "Mở liên kết sau để tạo mật khẩu mới:\n"
        f"{reset_url}\n\n"
        "Liên kết có hiệu lực 15 phút và chỉ sử dụng được một lần.\n"
        "Nếu bạn không yêu cầu, hãy bỏ qua email này. "
        "Mật khẩu hiện tại của bạn vẫn giữ nguyên.\n\n"
        "Mộc Hán"
    )

    with smtplib.SMTP(
        config["MAIL_SERVER"],
        config["MAIL_PORT"],
        timeout=20,
    ) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)