import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with  MySQL username
        password='--------',  # Replace with MySQL password
        database='evoting'  # Replace with the correct database name
    )
