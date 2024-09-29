class TipoUsuarioDTO:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def __repr__(self):
        return (f"TipoUsuarioDTO(id={self.id}, nombre={self.nombre})")

    def __str__(self):
        return (f"TipoUsuarioDTO({self.id}, {self.nombre})")