from dto import PrestamoSqlDTO
from dto import PrestamoTablaDTO
from dto import PrestamoDetalleDTO

from typing import List

class PrestamoDAO:
    def __init__(self, connection):
        self.connection = connection
    
    def cargar_todos_los_prestamos(self) -> List[PrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                p.id AS id_prestamo,
                p.id_solicitud,
                sp.id_empleado,
                MAX(pg.fecha_pago) AS fecha_ult_pago,
                p.saldo_pendiente,
                COALESCE(SUM(pg.monto_pagado), 0) AS saldo_acumulado,
                COUNT(pg.id) AS numero_pagos,
                p.fecha_aprobacion,
                p.fecha_vencimiento,
                p.estado_prestamo
            FROM 
                Prestamo p
            JOIN 
                SolicitudPrestamo sp ON p.id_solicitud = sp.id
            LEFT JOIN 
                Pago pg ON pg.id_prestamo = p.id
            GROUP BY 
                p.id, p.id_solicitud, sp.id_empleado, p.saldo_pendiente, p.fecha_aprobacion, p.fecha_vencimiento, p.estado_prestamo
            ORDER BY p.id
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            solicitudes_prestamos = [PrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(e)
            return []
    
    def cargar_prestamos_por_empleado(self, id_empleado) -> List[PrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT 
                p.id AS id_prestamo,
                p.id_solicitud,
                sp.id_empleado,
                MAX(pg.fecha_pago) AS fecha_ult_pago,
                p.saldo_pendiente,
                COALESCE(SUM(pg.monto_pagado), 0) AS saldo_acumulado,
                COUNT(pg.id) AS numero_pagos,
                p.fecha_aprobacion,
                p.fecha_vencimiento,
                p.estado_prestamo
            FROM 
                Prestamo p
            JOIN 
                SolicitudPrestamo sp ON p.id_solicitud = sp.id
            LEFT JOIN 
                Pago pg ON pg.id_prestamo = p.id
            WHERE 
                sp.id_empleado = :id_empleado
            GROUP BY 
                p.id, p.id_solicitud, sp.id_empleado, p.saldo_pendiente, p.fecha_aprobacion, p.fecha_vencimiento, p.estado_prestamo
            ORDER BY 
                p.id
            """
            cursor.execute(query, {"id_empleado": id_empleado})
            filas = cursor.fetchall()
            solicitudes_prestamos = [PrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return solicitudes_prestamos
        except Exception as e:
            print(e)
            return []
    
    def obtener_datos_solicitud_prestamo_por_id_prestamo(self, id_prestamo) -> PrestamoDetalleDTO:
        try:
            cursor = self.connection.cursor()
            # Consultar los datos del préstamo
            query = """
            SELECT s.monto, s.interes, s.periodo, p.saldo_pendiente, p.estado_prestamo, p.fecha_aprobacion 
            FROM SolicitudPrestamo s 
            JOIN Prestamo p ON s.id = p.id_solicitud 
            WHERE p.id = :id_prestamo
            """
            cursor.execute(query, {'id_prestamo': id_prestamo})
            fila = cursor.fetchone()
            cursor.close()
            return PrestamoDetalleDTO(*fila) if fila else None

        except Exception as e:
            print(e)

    def obtener_saldo_y_estado_prestamo(self, id_prestamo):
        cursor = self.connection.cursor()
        try:
            query = "SELECT saldo_pendiente, estado_prestamo FROM Prestamo WHERE id = :id_prestamo"
            cursor.execute(query, {'id_prestamo': id_prestamo})
            prestamo = cursor.fetchone()
            return prestamo  # Devuelve (saldo_pendiente, estado_prestamo) o None si no se encuentra.
        except Exception as e:
            print(f"Error al obtener saldo y estado del préstamo: {str(e)}")
            return None
        finally:
            cursor.close()

    def actualizar_saldo_y_estado_prestamo(self, id_prestamo, saldo_pendiente, estado):
        cursor = self.connection.cursor()
        try:
            query = """
                UPDATE Prestamo 
                SET saldo_pendiente = :saldo_pendiente, estado_prestamo = :estado
                WHERE id = :id_prestamo
            """
            cursor.execute(query, {
                'saldo_pendiente': saldo_pendiente,
                'estado': estado,
                'id_prestamo': id_prestamo
            })
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar saldo y estado del préstamo: {str(e)}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()


    def insertar_prestamo(self, prestamo: PrestamoSqlDTO):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Prestamo (id_solicitud, fecha_aprobacion, fecha_vencimiento, saldo_pendiente, estado_prestamo)
                VALUES (:1, :2, :3, :4, 'ACTIVO')
            """, (prestamo.id_solicitud, prestamo.fecha_aprobacion, prestamo.fecha_vencimiento, prestamo.saldo_pendiente))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            cursor.close()

    def cancelar_prestamo_por_id_solicitud(self, id_solicitud_prestamo):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Prestamo SET estado_prestamo = 'CANCELADO' WHERE id_solicitud = :1", (id_solicitud_prestamo,))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            raise e

    def buscar_prestamos(self, id_prestamo=None, id_solicitud=None, id_empleado=None, estado=None) -> List[PrestamoTablaDTO]:
        try:
            cursor = self.connection.cursor()
            
            # Crear una consulta SQL dinámica
            query = """
            SELECT 
                p.id AS id_prestamo,
                p.id_solicitud,
                sp.id_empleado,
                MAX(pg.fecha_pago) AS fecha_ult_pago,
                p.saldo_pendiente,
                COALESCE(SUM(pg.monto_pagado), 0) AS saldo_acumulado,
                COUNT(pg.id) AS numero_pagos,
                p.fecha_aprobacion,
                p.fecha_vencimiento,
                p.estado_prestamo
            FROM 
                Prestamo p
            JOIN 
                SolicitudPrestamo sp ON p.id_solicitud = sp.id
            LEFT JOIN 
                Pago pg ON pg.id_prestamo = p.id
            WHERE 1=1
            """
            
            # Agregar condiciones basadas en los filtros de búsqueda
            params = []
            if id_prestamo:
                query += " AND p.id = :1"
                params.append(id_prestamo)
            if id_solicitud:
                query += " AND p.id_solicitud = :2"
                params.append(id_solicitud)
            if id_empleado:
                query += " AND sp.id_empleado = :3"
                params.append(id_empleado)
            if estado:
                query += " AND p.estado_prestamo = :4"
                params.append(estado)

            query += """
            GROUP BY 
                p.id, p.id_solicitud, sp.id_empleado, p.saldo_pendiente, p.fecha_aprobacion, p.fecha_vencimiento, p.estado_prestamo
            ORDER BY p.id
            """
            cursor.execute(query, params)
            filas = cursor.fetchall()
            prestamos = [PrestamoTablaDTO(*fila) for fila in filas]
            cursor.close()
            return prestamos
        except Exception as e:
            print(e)
            return []