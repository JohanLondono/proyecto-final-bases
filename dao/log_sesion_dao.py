from dto import LogSesionSqlDTO
from dto import LogSesionTablaDTO
from typing import List
from datetime import datetime

class LogSesionDAO:
    def __init__(self, connection):
        self.connection = connection

    def registrar_log_sesion(self, log: LogSesionSqlDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO LogSesion (id_usuario, fecha, tipo, estado)
                VALUES (:id_usuario, :fecha, :tipo, :estado)
            """
            cursor.execute(query, {
                'id_usuario': log.id_usuario,
                'fecha': log.fecha,
                'tipo': log.tipo,
                'estado': log.estado
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar el Log de Sesion: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_logs_sesion(self) -> List[LogSesionTablaDTO]:
      
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                ls.id AS ID_LOG_SESION,
                ls.id_usuario AS ID_USUARIO,
                e.nombre AS NOMBRE_EMPLEADO,
                e.apellido AS APELLIDO_EMPLEADO,
                e.id_empleado AS ID_EMPLEADO,
                ls.fecha AS FECHA,
                ls.tipo AS TIPO,
                ls.estado AS ESTADO
            FROM 
                LogSesion ls
            JOIN 
                Usuario u ON ls.id_usuario = u.id_empleado
            JOIN 
                Empleado e ON u.id_empleado = e.id_empleado
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            logs_sesion = [LogSesionTablaDTO(*fila) for fila in filas]
            cursor.close()
            return logs_sesion
        except Exception as e:
            print(f"Error al cargar los registros de inicio de sesión: {e}")
            return []

    def buscar_logs(self, id_log=None, id_usuario=None, id_empleado=None, fecha_inicio=None, fecha_fin=None, tipo=None, estado=None) -> List[LogSesionTablaDTO]:
        """
        Busca registros de inicio de sesión en función de varios filtros opcionales.
        """
        consulta = """
        SELECT 
            ls.id AS ID_LOG_SESION,
            ls.id_usuario AS ID_USUARIO,
            e.nombre AS NOMBRE_EMPLEADO,
            e.apellido AS APELLIDO_EMPLEADO,
            e.id_empleado AS ID_EMPLEADO,
            ls.fecha AS FECHA,
            ls.tipo AS TIPO,
            ls.estado AS ESTADO
        FROM 
            LogSesion ls
        JOIN 
            Usuario u ON ls.id_usuario = u.id_empleado
        JOIN 
            Empleado e ON u.id_empleado = e.id_empleado
        WHERE 1=1
        """
        parametros = []

        if id_log:
            consulta += " AND ls.id = :1"
            parametros.append(id_log)
        if id_usuario:
            consulta += " AND ls.id_usuario = :2"
            parametros.append(id_usuario)
        if id_empleado:
            consulta += " AND e.id_empleado = :3"
            parametros.append(id_empleado)
        if fecha_inicio and fecha_fin:
            consulta += " AND ls.fecha BETWEEN :4 AND :5"
            parametros.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            consulta += " AND ls.fecha >= :4"
            parametros.append(fecha_inicio)
        elif fecha_fin:
            consulta += " AND ls.fecha <= :4"
            parametros.append(fecha_fin)
        if tipo:
            consulta += " AND ls.tipo = :6"
            parametros.append(tipo)
        if estado:
            consulta += " AND ls.estado = :7"
            parametros.append(estado)
        try:
            cursor = self.connection.cursor()
            cursor.execute(consulta, parametros)
            filas = cursor.fetchall()
            logs_sesion = [LogSesionTablaDTO(*fila) for fila in filas]
            cursor.close()
            return logs_sesion
        except Exception as e:
            print(f"Error al buscar registros de inicio de sesión: {e}")
            return []