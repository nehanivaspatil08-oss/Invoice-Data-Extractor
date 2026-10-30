
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

connection = None

try:
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "invoice_db")
    )

    if connection.is_connected():
        print("MySQL connection successful!")
        print("Connected database: invoice_db")

except Error as error:
    print("MySQL connection failed.")
    print("Error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("Connection closed.")
