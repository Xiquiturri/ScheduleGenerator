import datetime

class evento:
    def __init__(self,fecha,momento,cupo,default,obligado,participante=None):
        self._fecha = fecha
        self._momento = momento
        self._cupo = cupo
        self._default = default
        self._obligado = obligado
        self._participante = participante if participante is not None else set()
    
    #lectura - getter 
    @property
    def fecha(self):
        return self._fecha

    @property
    def momento(self):
        return self._momento
    
    @property
    def cupo(self):
        return self._cupo
    
    @property
    def default(self):
        return self._default
    
    @property 
    def obligado(self):
        return self._obligado
    
    @property
    def participante(self):
        return self._participante



    #escritura - setter
    @fecha.setter
    def fecha(self, value):
        self._fecha = value

    @momento.setter
    def momento(self,value):
        self._momento = value

    @cupo.setter
    def cupo(self,value):
        self._cupo = value
    
    @default.setter
    def default(self,value):
        self._default = value
    
    @obligado.setter
    def obligado(self,value):
        self._obligado = value

    @participante.setter
    def participante(self,value):
        self._participante = value