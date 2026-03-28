# test_db.py
import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='hiten@123',
        database='easybook_db'
    )
    print("✅ MySQL Connection Successful!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL Version: {version[0]}")
    
    connection.close()
except Exception as e:
    print(f"❌ Connection Failed: {e}")