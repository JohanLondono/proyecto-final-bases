class PagoSqlDTO:
    def __init__(self, id, id_prestamo, monto_pagado, fecha_pago, metodo_pago):
        self.id = id
        self.id_prestamo = id_prestamo
        self.monto_pagado = monto_pagado
        self.fecha_pago = fecha_pago
        self.metodo_pago = metodo_pago

    def __repr__(self):
        return (f"PagoSqlDTO(id={self.id}, id_prestamo={self.id_prestamo}, monto_pagado={self.monto_pagado}, "
                f"fecha_pago={self.fecha_pago}, metodo_pago={self.metodo_pago})")

    def __str__(self):
        return (f"PagoSqlDTO({self.id}, {self.id_prestamo}, {self.monto_pagado}, "
                f"{self.fecha_pago}, {self.metodo_pago})")