from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2
import redis

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'username': 'admin',
    'password': 'admin123',
    'database': 'frauddetection'
}

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'password': 'redis123',
    'db': 0
}

def get_database_connection():
    connection_string = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    
    engine = create_engine(connection_string)
    
    Session = sessionmaker(bind=engine)
    return Session()

def execute_query(query, params=None):
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database']
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
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database']
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
    return psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database']
    ) 