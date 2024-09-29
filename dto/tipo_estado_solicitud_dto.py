class TipoEstadoSolicitudDTO:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre


    def __repr__(self):
        return (f"TipoEstadoSolicitudDTO(id={self.id}, nombre={self.nombre})")

    def __str__(self):
        return (f"TipoEstadoSolicitudDTO({self.id}, {self.nombre})")