import pandas as pd
from sqlalchemy import create_engine

class ReporteDAO:
    def __init__(self, engine):
        self.engine = engine

    def generar_morosos(self):
        query = """
        SELECT 
            e.id_empleado, 
            e.nombre, 
            e.apellido, 
            sp.monto, 
            tp.meses AS periodo, 
            tp.interes, 
            p.id AS id_prestamo, 
            p.fecha_aprobacion, 
            tep.nombre AS estado_prestamo
        FROM 
            Empleado e
        JOIN 
            SolicitudPrestamo sp ON e.id_empleado = sp.id_empleado
        JOIN 
            TipoPeriodo tp ON sp.id_tipo_periodo = tp.id
        JOIN 
            Prestamo p ON p.id_solicitud = sp.id
        JOIN 
            TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id
        WHERE 
            tep.nombre NOT IN ('PAGADO', 'CANCELADO')
        """
        return pd.read_sql_query(query, self.engine)

    def generar_total_prestado_por_municipio(self):
        query = """
        SELECT 
            dep.nombre as departamento, 
            mu.nombre as municipio, 
            SUM(sp.monto) AS total_prestado
        FROM 
            Prestamo p
        JOIN 
            SolicitudPrestamo sp ON p.id_solicitud = sp.id
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        JOIN 
            Empleado e ON sp.id_empleado = e.id_empleado
        JOIN 
            Sucursal s ON e.sucursal_codigo = s.codigo
        JOIN 
            Municipio mu ON s.id_municipio = mu.id
        JOIN 
            Departamento dep ON mu.id_departamento = dep.id
        WHERE 
            (tes.nombre = 'APROBADA' OR tes.nombre = 'CANCELADA')
        GROUP BY 
            dep.nombre, mu.nombre
        ORDER BY 
            dep.nombre
        """
        return pd.read_sql_query(query, self.engine)

    def generar_total_prestado_por_sucursal(self):
        query = """
        SELECT 
            s.codigo, 
            s.nombre, 
            dep.nombre AS departamento, 
            mu.nombre AS municipio, 
            SUM(sp.monto) AS total_prestado
        FROM 
            Prestamo p
        JOIN 
            SolicitudPrestamo sp ON p.id_solicitud = sp.id
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        JOIN 
            Empleado e ON sp.id_empleado = e.id_empleado
        JOIN 
            Sucursal s ON e.sucursal_codigo = s.codigo
        JOIN 
            Municipio mu ON s.id_municipio = mu.id
        JOIN 
            Departamento dep ON mu.id_departamento = dep.id
        WHERE 
            (tes.nombre = 'APROBADA' OR tes.nombre = 'CANCELADA')
        GROUP BY 
            s.codigo, 
            s.nombre, 
            dep.nombre, 
            mu.nombre
        ORDER BY 
            dep.nombre
        """
        return pd.read_sql_query(query, self.engine)

    def generar_prestamos_por_empleado(self):
        query = """
        SELECT 
            p.id AS id_prestamo, 
            e.id_empleado, 
            e.nombre, 
            e.apellido, 
            SUM(sp.monto) AS total_prestado, 
            p.saldo_pendiente, 
            COUNT(pg.id) AS numero_pagos,
            tep.nombre AS estado_prestamo
        FROM 
            Empleado e
        JOIN 
            SolicitudPrestamo sp ON e.id_empleado = sp.id_empleado
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        JOIN 
            Prestamo p ON p.id_solicitud = sp.id
        JOIN 
            TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id        
        LEFT JOIN 
            Pago pg ON pg.id_prestamo = p.id
        WHERE 
            (tes.nombre = 'APROBADA' OR tes.nombre = 'CANCELADA')
        GROUP BY 
            e.id_empleado, 
            e.nombre, 
            e.apellido, 
            p.saldo_pendiente, 
            p.id, 
            tep.nombre
        ORDER BY 
            e.id_empleado
        """
        return pd.read_sql_query(query, self.engine)
    
    def generar_total_prestamos_y_saldo_por_empleado(self):
        query = """
        SELECT 
            e.id_empleado, 
            e.nombre, 
            e.apellido, 
            SUM(sp.monto) AS total_prestado, 
            SUM(p.saldo_pendiente) AS saldo_pendiente_total,
            COUNT(p.id) AS numero_prestamos
        FROM 
            Empleado e
        JOIN 
            SolicitudPrestamo sp ON e.id_empleado = sp.id_empleado
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        JOIN 
            Prestamo p ON p.id_solicitud = sp.id
        WHERE 
            tes.nombre IN ('APROBADA', 'CANCELADA')
        GROUP BY 
            e.id_empleado, e.nombre, e.apellido
        ORDER BY 
            total_prestado DESC
        """
        return pd.read_sql_query(query, self.engine)

    def generar_total_estados_solicitud_prestamos(self):
        query = """
        SELECT 
            tes.nombre as estado, 
            COUNT(sp.id) AS total
        FROM 
            SolicitudPrestamo sp
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        GROUP BY 
            tes.nombre
        """
        return pd.read_sql_query(query, self.engine)

    def generar_total_estados_prestamos(self):
        query = """
        SELECT tep.nombre as estado_prestamo, 
            COUNT(p.id) AS total
        FROM 
            Prestamo p
        JOIN 
            TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id        
        GROUP BY 
            tep.nombre
        """
        return pd.read_sql_query(query, self.engine)

    def generar_pagos_por_empleado(self):
        query = """
        SELECT 
            pg.id AS id_pago, 
            e.id_empleado, 
            e.nombre, 
            e.apellido, 
            pg.monto_pagado, 
            pg.fecha_pago, 
            tpp.nombre as metodo_pago
        FROM 
            Empleado e
        JOIN 
            SolicitudPrestamo sp ON e.id_empleado = sp.id_empleado
        JOIN 
            Prestamo p ON sp.id = p.id_solicitud
        JOIN 
            Pago pg ON p.id = pg.id_prestamo
        JOIN 
            Tipopago tpp ON pg.id_tipo_pago = tpp.id
        ORDER BY 
            e.id_empleado
        """
        return pd.read_sql_query(query, self.engine)
    
    def generar_total_pagado_y_numero_pagos_por_empleado(self):
        query = """
        SELECT 
            e.id_empleado, 
            e.nombre, 
            e.apellido, 
            SUM(pg.monto_pagado) AS total_pagado,
            COUNT(pg.id) AS numero_pagos
        FROM 
            Empleado e
        JOIN 
            SolicitudPrestamo sp ON e.id_empleado = sp.id_empleado
        JOIN 
            Prestamo p ON sp.id = p.id_solicitud
        JOIN 
            Pago pg ON p.id = pg.id_prestamo
        GROUP BY 
            e.id_empleado, 
            e.nombre, 
            e.apellido
        ORDER BY 
            e.id_empleado
        """
        return pd.read_sql_query(query, self.engine)

    def generar_ganancias_por_intereses(self):
        query = """
        SELECT 
            p.id AS id_prestamo,
            ROUND(sp.monto, 3) AS monto, 
            ROUND(SUM(pg.monto_pagado), 3) AS total_pagado, 
            -- Redondeo de la cuota con interés
            ROUND((sp.monto + (sp.monto * (tp.interes / 100))) / tp.meses, 3) AS cuota_con_interes,
            -- Redondeo de la cuota sin interés
            ROUND((sp.monto / tp.meses), 3) AS cuota_sin_interes,
            -- Número de cuotas que representa el total_pagado
            ROUND(SUM(pg.monto_pagado) / ((sp.monto + (sp.monto * (tp.interes / 100))) / tp.meses), 3) AS numero_cuotas,
            -- Identifica si el total pagado cubre o excede el monto del préstamo
            CASE 
                WHEN sp.monto <= SUM(pg.monto_pagado) THEN 'PAGO_TOTAL'
                ELSE 'CUOTAS'
            END AS tipo_pago,
            -- Cálculo de los intereses ganados
            CASE 
                -- Para pagos parciales (cuotas), calculamos el interés acumulado
                WHEN sp.monto > SUM(pg.monto_pagado) THEN 
                    ROUND(
                    -- Calcula el número de cuotas pagadas usando la cuota con interés
                    ((sp.monto * (1 + (tp.interes / 100)) / tp.meses) - (sp.monto / tp.meses)) * 
                    (SUM(pg.monto_pagado) / ((sp.monto + (sp.monto * (tp.interes / 100))) / tp.meses)), 3)
                -- Para pagos totales, calculamos los intereses sobre el préstamo completo
                ELSE 
                    ROUND((sp.monto * (1 + (tp.interes / 100))) - sp.monto, 3)
            END AS intereses_ganados
        FROM 
            SolicitudPrestamo sp
        JOIN 
            TipoPeriodo tp ON sp.id_tipo_periodo = tp.id
        JOIN 
            Prestamo p ON sp.id = p.id_solicitud
        JOIN 
            Pago pg ON p.id = pg.id_prestamo
        GROUP BY 
            p.id, sp.monto, tp.meses, tp.interes
        ORDER BY 
            p.id
        """
        return pd.read_sql_query(query, self.engine)

    def generar_total_prestado_por_banco(self):
        query = """
        SELECT 
            SUM(sp.monto) AS total_prestado
        FROM 
            Prestamo p
        JOIN 
            SolicitudPrestamo sp ON p.id_solicitud = sp.id
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        WHERE 
            tes.nombre IN ('APROBADA', 'CANCELADA')
        """
        return pd.read_sql_query(query, self.engine)

    
    def generar_grafica_prestamos_por_estado(self):
        query = """
        SELECT 
            tep.nombre AS estado_prestamo, 
            COUNT(p.id) AS total
        FROM 
            Prestamo p
        JOIN 
            TipoEstadoPrestamo tep ON p.id_tipo_estado_prestamo = tep.id        
        GROUP BY 
            tep.nombre
        """
        return pd.read_sql_query(query, self.engine)

    def generar_grafica_total_prestado_y_prestamos_por_empleado(self):
        query = """
        SELECT 
            e.id_empleado, 
            SUM(sp.monto) AS total_prestado, 
            COUNT(p.id) AS num_prestamos
        FROM 
            Prestamo p
        JOIN 
            SolicitudPrestamo sp ON p.id_solicitud = sp.id
        JOIN 
            TipoEstadoSolicitud tes ON sp.id_tipo_estado_solicitud = tes.id
        JOIN 
            Empleado e ON sp.id_empleado = e.id_empleado
        WHERE 
            (tes.nombre = 'APROBADA' OR tes.nombre = 'CANCELADA')
        GROUP BY 
            e.id_empleado
        ORDER BY 
            total_prestado DESC
        """
        return pd.read_sql_query(query, self.engine)