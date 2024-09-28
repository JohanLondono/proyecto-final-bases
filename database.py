import cx_Oracle
from sqlalchemy import create_engine

def get_connection():
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='XE')
    user = 'system'
    password = 'admin123'
    try:
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Error conectando a la base de datos: {e}")
        return None
    
def create_sqlalchemy_engine():
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='XE')
    user = 'system'
    password = 'admin123'
    
    connection_string = f'oracle+cx_oracle://{user}:{password}@{dsn_tns}'
    engine = create_engine(connection_string)
    
    return engine