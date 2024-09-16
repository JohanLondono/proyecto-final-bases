class LogSesionSqlDTO:
    def __init__(self, id, id_usuario, fecha, tipo, estado):
        self.id = id              
        self.id_usuario = id_usuario   
        self.fecha = fecha        
        self.tipo = tipo        
        self.estado = estado    


    def __repr__(self):
        return (f"LogSesionSqlDTO(id={self.id}, id_usuario={self.id_usuario}, "
                f"fecha={self.fecha}, tipo={self.tipo}, estado={self.estado})")

    def __str__(self):
        return (f"LogSesionSqlDTO({self.id}, {self.id_usuario}, {self.fecha}, {self.tipo}, {self.estado})")