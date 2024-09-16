import cx_Oracle

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