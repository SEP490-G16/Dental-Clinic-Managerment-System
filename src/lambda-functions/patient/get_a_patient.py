import pyodbc
import json

# Cấu hình kết nối
server = 'your_server_name'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'
# tên driver có thể cần điều chỉnh tùy vào phiên bản
driver = '{ODBC Driver 17 for SQL Server}'

# Thiết lập kết nối
cnxn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()


def lambda_handler(event, context):

    # Thực hiện truy vấn đơn giản
    cursor.execute("SELECT TOP 5 * FROM Patient")
    rows = cursor.fetchall()

    # Chuyển đổi kết quả truy vấn thành JSON
    result = [dict(zip([column[0] for column in cursor.description], row))
              for row in rows]

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
