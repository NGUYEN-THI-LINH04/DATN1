from contextlib import closing
from getpass import getpass

import pyodbc
from werkzeug.security import generate_password_hash

from database import get_connection
from routes.auth import USERNAME_PATTERN, valid_email


def main():
    print("TAO TAI KHOAN QUAN TRI VIEN")

    username = input("Ten dang nhap admin: ").strip()
    full_name = input("Ho va ten: ").strip()
    email = input("Email: ").strip().lower()

    if USERNAME_PATTERN.fullmatch(username) is None:
        print(
            "Ten dang nhap can 3-50 ky tu: "
            "chu khong dau, so, dau cham, gach duoi hoac gach ngang."
        )
        return

    if not 2 <= len(full_name) <= 150:
        print("Ho ten can tu 2 den 150 ky tu.")
        return

    if not valid_email(email):
        print("Email khong hop le.")
        return

    password = getpass("Mat khau admin: ")
    confirm_password = getpass("Nhap lai mat khau: ")

    if not 8 <= len(password) <= 128:
        print("Mat khau can tu 8 den 128 ky tu.")
        return

    if password != confirm_password:
        print("Mat khau nhap lai khong khop.")
        return

    password_hash = generate_password_hash(password)

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    """
                    INSERT INTO dbo.QuanTriVien
                        (
                            TenDangNhap,
                            ThuDienTu,
                            MatKhauBam,
                            HoTen
                        )
                    VALUES (?, ?, ?, ?);
                    """,
                    (
                        username,
                        email,
                        password_hash,
                        full_name,
                    ),
                )

            connection.commit()

    except pyodbc.IntegrityError:
        print(
            "Ten dang nhap hoac email admin da ton tai. "
            "Khong thay doi tai khoan cu."
        )
        return

    except pyodbc.Error:
        print(
            "Khong tao duoc admin. "
            "Hay chay python database.py de kiem tra ket noi."
        )
        return

    print("TAO ADMIN THANH CONG!")
    print(f"Ten dang nhap: {username}")
    print("Ban co the dang nhap tai /admin/dang-nhap")


if __name__ == "__main__":
    main()