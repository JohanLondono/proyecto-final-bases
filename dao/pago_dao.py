from dto import PagoSqlDTO
from dto import PagoTablaDTO
from typing import List
from datetime import datetime

class PagoDAO:
    def __init__(self, connection):
        self.connection = connection
        
    def obtener_fecha_ultimo_pago(self, id_prestamo):
        try:
            # Consulta para obtener la última fecha de pago del préstamo
            cursor = self.connection.cursor()
            query = """
            SELECT MAX(fecha_pago) 
            FROM Pago 
            WHERE id_prestamo = :id_prestamo
            """
            cursor.execute(query, {'id_prestamo': id_prestamo})
            fecha_ultimo_pago = cursor.fetchone()[0]
            cursor.close()
            return fecha_ultimo_pago
        except Exception as e:
            print(e)
            

    def registrar_pago(self, pago: PagoSqlDTO):
     
        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO Pago (id_prestamo, monto_pagado, fecha_pago, metodo_pago)
                VALUES (:id_prestamo, :monto_pagado, :fecha_pago, :metodo_pago)
            """
            cursor.execute(query, {
                'id_prestamo': pago.id_prestamo,
                'monto_pagado': pago.monto_pagado,
                'fecha_pago': pago.fecha_pago,
                'metodo_pago': pago.metodo_pago
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al registrar pago: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def cargar_todos_los_pagos(self) -> List[PagoTablaDTO]:
        """
        Carga todos los pagos de la base de datos y los convierte en objetos PagoDTO.
        """
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                p.id AS ID_PAGO, 
                p.id_prestamo AS ID_PRESTAMO, 
                sp.id_empleado AS ID_EMPLEADO, 
                p.monto_pagado AS MONTO_PAGADO, 
                p.fecha_pago AS FECHA_PAGO, 
                p.metodo_pago AS METODO_PAGO
            FROM 
                Pago p
            JOIN 
                Prestamo pr ON p.id_prestamo = pr.id
            JOIN 
                SolicitudPrestamo sp ON pr.id_solicitud = sp.id
            ORDER BY
                p.fecha_pago
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            pagos = [PagoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar todos los pagos: {e}")
            return []

    def cargar_pagos_por_empleado(self, id_empleado: int) -> List[PagoTablaDTO]:
        """
        Carga todos los pagos realizados por un empleado específico a través de su ID.
        """
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                p.id AS ID_PAGO, 
                p.id_prestamo AS ID_PRESTAMO, 
                sp.id_empleado AS ID_EMPLEADO, 
                p.monto_pagado AS MONTO_PAGADO, 
                p.fecha_pago AS FECHA_PAGO, 
                p.metodo_pago AS METODO_PAGO
            FROM 
                Pago p
            JOIN 
                Prestamo pr ON p.id_prestamo = pr.id
            JOIN 
                SolicitudPrestamo sp ON pr.id_solicitud = sp.id
            WHERE 
                sp.id_empleado = :1
            ORDER BY
                p.fecha_pago
            """
            cursor.execute(query, (id_empleado,))
            filas = cursor.fetchall()
            pagos = [PagoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al cargar los pagos del empleado con ID {id_empleado}: {e}")
            return []

    def buscar_pagos(self, id_pago=None, id_prestamo=None, id_empleado=None, fecha_inicio=None, fecha_fin=None) -> List[PagoTablaDTO]:
        """
        Busca pagos en función de varios filtros opcionales.
        """
        consulta = """
        SELECT 
            p.id AS ID_PAGO, 
            p.id_prestamo AS ID_PRESTAMO, 
            sp.id_empleado AS ID_EMPLEADO, 
            p.monto_pagado AS MONTO_PAGADO, 
            p.fecha_pago AS FECHA_PAGO, 
            p.metodo_pago AS METODO_PAGO
        FROM 
            Pago p
        JOIN 
            Prestamo pr ON p.id_prestamo = pr.id
        JOIN 
            SolicitudPrestamo sp ON pr.id_solicitud = sp.id
        WHERE 1=1
        """
        parametros = []

        if id_pago:
            consulta += " AND p.id = :1"
            parametros.append(id_pago)
        if id_prestamo:
            consulta += " AND p.id_prestamo = :2"
            parametros.append(id_prestamo)
        if id_empleado:
            consulta += " AND sp.id_empleado = :3"
            parametros.append(id_empleado)
        if fecha_inicio and fecha_fin:
            consulta += " AND p.fecha_pago BETWEEN :4 AND :5"
            parametros.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            consulta += " AND p.fecha_pago >= :4"
            parametros.append(fecha_inicio)
        elif fecha_fin:
            consulta += " AND p.fecha_pago <= :4"
            parametros.append(fecha_fin)

        try:
            cursor = self.connection.cursor()
            cursor.execute(consulta, parametros)
            filas = cursor.fetchall()
            pagos = [PagoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return pagos
        except Exception as e:
            print(f"Error al buscar pagos: {e}")
            return []