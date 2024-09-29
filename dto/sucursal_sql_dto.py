class SucursalSqlDTO:
    def __init__(self, codigo, id_municipio, nombre, presupuesto):
        self.codigo = codigo
        self.id_municipio = id_municipio
        self.nombre = nombre
        self.presupuesto = presupuesto

    def __repr__(self):
        return (f"SucursalSqlDTO(codigo={self.codigo}, id_municipio={self.id_municipio}, "
                f"nombre={self.nombre}, presupuesto={self.presupuesto})")

    def __str__(self):
        return (f"SucursalSqlDTO({self.codigo}, {self.id_municipio}, {self.nombre}, "
                f"{self.presupuesto})")