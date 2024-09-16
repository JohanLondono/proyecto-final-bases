class PrestamoTablaDTO:
    def __init__(self, id, id_solicitud, id_empleado, fecha_ult_pago, saldo_pendiente, saldo_acumulado, numero_pagos, fecha_aceptacion, fecha_vencimiento, estado_prestamo):
        self.id = id
        self.id_solicitud = id_solicitud
        self.id_empleado = id_empleado
        self.fecha_ult_pago = fecha_ult_pago
        self.saldo_pendiente = saldo_pendiente
        self.saldo_acumulado = saldo_acumulado
        self.numero_pagos = numero_pagos
        self.fecha_aceptacion = fecha_aceptacion
        self.fecha_vencimiento = fecha_vencimiento
        self.estado_prestamo = estado_prestamo

    def __repr__(self):
        return (f"PrestamoTablaDTO(id={self.id}, id_solicitud={self.id_solicitud}, id_empleado={self.id_empleado}, "
                f"fecha_ult_pago={self.fecha_ult_pago}, saldo_pendiente={self.saldo_pendiente}, saldo_acumulado={self.saldo_acumulado}, numero_pagos={self.numero_pagos} "
                f"fecha_aceptacion={self.fecha_aceptacion}, fecha_vencimiento={self.fecha_vencimiento}, estado_prestamo={self.estado_prestamo})")

    def __str__(self):
        return (f"PrestamoTablaDTO({self.id}, {self.id_solicitud}, {self.id_empleado}, "
                f"{self.fecha_ult_pago}, {self.saldo_pendiente}, {self.saldo_acumulado}, {self.numero_pagos} "
                f"{self.fecha_aceptacion}, {self.fecha_vencimiento}, {self.estado_prestamo})")