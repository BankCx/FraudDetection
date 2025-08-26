from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg
import redis
import os

DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'username': os.getenv('DATABASE_USERNAME', 'admin'),
    'password': os.getenv('DATABASE_PASSWORD', 'admin123'),
    'database': os.getenv('DATABASE_NAME', 'frauddetection')
}

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'password': os.getenv('REDIS_PASSWORD', 'redis123'),
    'db': int(os.getenv('REDIS_DB', 0))
}

def get_database_connection():
    connection_string = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    
    engine = create_engine(connection_string)
    
    Session = sessionmaker(bind=engine)
    return Session()

def execute_query(query, params=None):
    conn = psycopg.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        dbname=DATABASE_CONFIG['database']
    )
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

def get_redis_connection():
    return redis.Redis(
        host=REDIS_CONFIG['host'],
        port=REDIS_CONFIG['port'],
        password=REDIS_CONFIG['password'],
        db=REDIS_CONFIG['db'],
        decode_responses=True
    )

def execute_transaction(queries):
    conn = psycopg.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        dbname=DATABASE_CONFIG['database']
    )
    try:
        cursor = conn.cursor()
        for query in queries:
            cursor.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Transaction error: {str(e)}")
        raise e
    finally:
        cursor.close()
        conn.close()

def get_raw_connection():
    return psycopg.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        dbname=DATABASE_CONFIG['database']
    ) 