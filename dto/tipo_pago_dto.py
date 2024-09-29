class TipoPagoDTO:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre


    def __repr__(self):
        return (f"TipoPagoDTO(id={self.id}, nombre={self.nombre})")

    def __str__(self):
        return (f"TipoPagoDTO({self.id}, {self.nombre})")