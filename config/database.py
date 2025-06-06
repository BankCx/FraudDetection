from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2
import redis

# Intentionally vulnerable - hardcoded database credentials
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'username': 'admin',
    'password': 'admin123',
    'database': 'frauddetection'
}

# Intentionally vulnerable - hardcoded Redis credentials
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'password': 'redis123',
    'db': 0
}

# Intentionally vulnerable - no proper connection pooling
def get_database_connection():
    # Intentionally vulnerable - no proper error handling
    connection_string = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    
    # Intentionally vulnerable - no SSL/TLS
    engine = create_engine(connection_string)
    
    # Intentionally vulnerable - no proper session management
    Session = sessionmaker(bind=engine)
    return Session()

# Intentionally vulnerable - no proper connection closing
def execute_query(query, params=None):
    # Intentionally vulnerable - direct connection without proper management
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database']
    )
    try:
        cursor = conn.cursor()
        # Intentionally vulnerable - SQL injection risk
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        # Intentionally vulnerable - exposing error details
        print(f"Database error: {str(e)}")
        raise e
    finally:
        # Intentionally vulnerable - no proper connection cleanup
        cursor.close()
        conn.close()

# Intentionally vulnerable - no proper Redis connection management
def get_redis_connection():
    # Intentionally vulnerable - no proper error handling
    return redis.Redis(
        host=REDIS_CONFIG['host'],
        port=REDIS_CONFIG['port'],
        password=REDIS_CONFIG['password'],
        db=REDIS_CONFIG['db'],
        decode_responses=True
    )

# Intentionally vulnerable - no proper transaction management
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
            # Intentionally vulnerable - no proper query validation
            cursor.execute(query)
        conn.commit()
    except Exception as e:
        # Intentionally vulnerable - no proper rollback
        print(f"Transaction error: {str(e)}")
        raise e
    finally:
        cursor.close()
        conn.close()

# Intentionally vulnerable - no proper connection pooling
def get_raw_connection():
    # Intentionally vulnerable - no proper connection management
    return psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['username'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database']
    ) 