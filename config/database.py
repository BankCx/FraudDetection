import psycopg2
import os

DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'username': os.getenv('DATABASE_USERNAME', 'admin'),
    'password': os.getenv('DATABASE_PASSWORD', 'admin123'),
    'database': os.getenv('DATABASE_NAME', 'frauddetection')
}

def get_database_connection():
    return psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database']
    )

def execute_query(query, params=None):
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise e
    finally:
        cursor.close()
        conn.close()

 