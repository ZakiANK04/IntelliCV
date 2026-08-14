"""
Database initialization script
Creates the MySQL database and tables
"""
import pymysql
from config import Config


def create_database():
    """Create the MySQL database if it doesn't exist"""
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # Create database
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"Database '{Config.MYSQL_DB}' created successfully!")
    finally:
        connection.close()


if __name__ == '__main__':
    print("Creating database...")
    create_database()
    print("Done!")
