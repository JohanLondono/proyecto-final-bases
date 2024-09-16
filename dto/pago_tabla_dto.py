class PagoTablaDTO:
    def __init__(self, id, id_prestamo, id_empleado, monto_pagado, fecha_pago, metodo_pago):
        self.id = id
        self.id_prestamo = id_prestamo
        self.id_empleado = id_empleado
        self.monto_pagado = monto_pagado
        self.fecha_pago = fecha_pago
        self.metodo_pago = metodo_pago

    def __repr__(self):
        return (f"PagoTablaDTO(id={self.id}, id_prestamo={self.id_prestamo}, id_empleado={self.id_empleado}, "
                f"monto_pagado={self.monto_pagado}, fecha_pago={self.fecha_pago}, metodo_pago={self.metodo_pago})")

    def __str__(self):
        return (f"PagoTablaDTO({self.id}, {self.id_prestamo}, {self.id_empleado}, "
                f"{self.monto_pagado}, {self.fecha_pago}, {self.metodo_pago})")