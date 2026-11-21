from contextlib import closing

import pyodbc

from config import Config


def get_odbc_driver():
    """Tìm driver SQL Server đã cài trên máy."""
    installed_drivers = pyodbc.drivers()

    for driver in (
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
    ):
        if driver in installed_drivers:
            return driver

    raise RuntimeError(
        "Chua co ODBC Driver 18 hoac 17 for SQL Server. "
        "Can cai Microsoft ODBC Driver 18 ban x64."
    )


def escape_odbc_value(value):
    """Xử lý ký tự đặc biệt trong thông tin kết nối."""
    return "{" + str(value).replace("}", "}}") + "}"


def get_connection():
    """Tạo kết nối mới tới SQL Server."""
    settings = {
        "DB_SERVER": Config.DB_SERVER,
        "DB_NAME": Config.DB_NAME,
        "DB_USER": Config.DB_USER,
        "DB_PASSWORD": Config.DB_PASSWORD,
    }

    missing = [
        name
        for name, value in settings.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Thieu thong tin trong .env: " + ", ".join(missing)
        )

    if Config.DB_PASSWORD == "MAT_KHAU_THAT_CUA_BAN":
        raise RuntimeError(
            "Ban chua dien mat khau SQL Server vao file .env."
        )

    driver = get_odbc_driver()

    connection_string = (
        f"DRIVER={escape_odbc_value(driver)};"
        f"SERVER={escape_odbc_value(Config.DB_SERVER)};"
        f"DATABASE={escape_odbc_value(Config.DB_NAME)};"
        f"UID={escape_odbc_value(Config.DB_USER)};"
        f"PWD={escape_odbc_value(Config.DB_PASSWORD)};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(
        connection_string,
        timeout=10,
        autocommit=False,
    )


def test_connection():
    """Kiểm tra kết nối, chỉ đọc và không sửa dữ liệu."""
    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    CONVERT(nvarchar(128), SERVERPROPERTY('ServerName')),
                    DB_NAME(),
                    SUSER_SNAME();
                """
            )

            server_name, database_name, login_name = cursor.fetchone()

            print("KET NOI SQL SERVER THANH CONG!")
            print(f"Server: {server_name}")
            print(f"Database: {database_name}")
            print(f"Tai khoan: {login_name}")

            cursor.execute(
                """
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME;
                """
            )

            tables = cursor.fetchall()

            print(f"\nSo bang: {len(tables)}")

            for schema_name, table_name in tables:
                print(f" - {schema_name}.{table_name}")


if __name__ == "__main__":
    try:
        test_connection()

    except RuntimeError as error:
        print(f"LOI CAU HINH: {error}")
        raise SystemExit(1)

    except pyodbc.Error as error:
        print("KET NOI SQL SERVER THAT BAI.")
        print(error)
        raise SystemExit(1)