class TipoEstadoPrestamoDTO:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre


    def __repr__(self):
        return (f"TipoEstadoPrestamoDTO(id={self.id}, nombre={self.nombre})")

    def __str__(self):
        return (f"TipoEstadoPrestamoDTO({self.id}, {self.nombre})")