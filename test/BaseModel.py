"""

"""
from abc import ABCMeta, abstractmethod
from typing import Union,Any,Dict
from datetime import datetime


class BaseModel(object):
    """
    Clase base para todos los modelos.

    Esta clase debera ser usada como base a todas las demas que definan modelo, basicamente
    define todos los campos que un registro contendra siempre , tales como activo,usuario,
    usuario_mod,fecha_creacion y fecha_modificacion. id representara el unique id del registro
    el cual debe existir.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.__activo = True  # type: bool
        self.usuario = None  # type: str
        self.usuario_mod = None   # type: str
        self.fecha_creacion = None # type: datetime
        self.fecha_modificacion = None # type: datetime

    @property
    def activo(self):
        # type: () -> bool
        """
        Property decorator para usar el estilo property para activo.

        Retorna si el registro que representa este modelo esta activo.
        """
        print("Getting value")
        return self.__activo

    @activo.setter
    def activo(self, value):
        # type: (bool) -> None
        """
        Metodo que manipula el campo activo.

        Ese metodo se usara para indicar si el registro representado por este modelo
        esta o no activo.
        """
        print("Setting value")
        if isinstance(value, bool):
            self.__activo = value
        else:
            self.__activo = False

    @activo.deleter
    def activo(self):
        del self.__activo

    def set_values(self, record):
        # type: (Dict[str,Any]) -> None
        if isinstance(record, dict):
            for field, value in record.items():
                if hasattr(self, field):
                    setattr(self, field, value)
        else:
            raise TypeError('record parameter need to be a dictionary of column names and values')

    @abstractmethod
    def get_pk_fields(self):
        # type: () -> Any
        pass

    def is_UID_pk(self):
        # type: () -> bool
        return False


class MyTestModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.testfield = None # type: Union[int, str]
        self.modelo = None # type: str

    def get_unique_id(self):
        return "dddd"

if __name__ == "__main__":
    modelo = MyTestModel()
    print(modelo.activo)
    modelo.activo = True
    modelo.usuario = "Usuario"
    modelo.fecha_creacion = "sss"
    modelo.id = "dd"
    modelo.id = BaseModel()
    modelo.id = 1000000000000000

    dict2 = {u'VERSION': u'HIGH ROOF A/C 2KD', u'modelo': u'HIACE', u'MARCA': u'TOYOTA','testfield':'Soy Test'}
   # dict2 = ('dddd','ffffff')
    modelo.set_values(dict2)

    test = modelo.id + 100
    print(modelo.id)
    print(test)
    print(modelo.activo)
    print(modelo.__dict__)
    print(hasattr(modelo, 'activo'))
    print(datetime.strptime('2012-03-30', "%Y-%m-%d").isoformat())
    print(datetime.now())

