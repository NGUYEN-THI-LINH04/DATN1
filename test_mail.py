import smtplib

from app import app
from mail_service import send_reset_email


with app.app_context():
    username = app.config.get("MAIL_USERNAME", "")
    password = app.config.get("MAIL_PASSWORD", "")

    print("Da doc email gui:", bool(username))
    print("Da doc mat khau ung dung:", bool(password))

    recipient = input(
        "Nhap email ban mo duoc hop thu de nhan thu thu: "
    ).strip()

    if not recipient:
        print("Ban chua nhap email nhan.")
        raise SystemExit(1)

    try:
        # Chỉ thử gửi thư, không tạo mã và không đổi mật khẩu.
        send_reset_email(
            recipient,
            "http://127.0.0.1:5000/quen-mat-khau",
        )

        print("MAY CHU EMAIL DA CHAP NHAN THU.")
        print("Hay mo hop thu den va thu rac cua email vua nhap.")
        print("Day la thu thu, lien ket khong phai ma dat lai mat khau.")

    except RuntimeError:
        print(
            "LOI CAU HINH: Chua doc duoc email/mat khau, "
            "hoac MAIL_PASSWORD van la gia tri mau."
        )

    except smtplib.SMTPAuthenticationError as error:
        print("LOI XAC THUC GMAIL. Ma loi:", error.smtp_code)
        print(
            "Kiem tra mat khau ung dung Google "
            "co thuoc dung MAIL_USERNAME hay khong."
        )

    except smtplib.SMTPRecipientsRefused:
        print("MAY CHU TU CHOI DIA CHI EMAIL NHAN.")

    except smtplib.SMTPException as error:
        print("LOI GUI MAIL:", type(error).__name__)
        print("Ma loi:", getattr(error, "smtp_code", "Khong co"))

    except OSError as error:
        print("LOI KET NOI MANG:", type(error).__name__)