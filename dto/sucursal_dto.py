class SucursalDTO:
    def __init__(self, codigo, nombre, departamento, municipio, director, presupuesto):
        self.codigo = codigo
        self.nombre = nombre
        self.departamento = departamento
        self.municipio = municipio
        self.director = director
        self.presupuesto = presupuesto

    def __repr__(self):
        return (f"SucursalDTO(codigo={self.codigo}, nombre={self.nombre}, "
                f"departamento={self.departamento}, municipio={self.municipio}, "
                f"director={self.director}, presupuesto={self.presupuesto})")

    def __str__(self):
        return (f"SucursalDTO({self.nombre}, {self.municipio}, "
                f"{self.director}, {self.presupuesto})")