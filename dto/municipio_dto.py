class MunicipioDTO:
    def __init__(self, id, id_departamento, nombre):
        self.id = id
        self.id_departamento = id_departamento
        self.nombre = nombre


    def __repr__(self):
        return (f"MunicipioDTO(id={self.id}, id_departamento={self.id_departamento}, nombre={self.nombre})")

    def __str__(self):
        return (f"MunicipioDTO({self.id}, {self.id_departamento}, {self.nombre})")