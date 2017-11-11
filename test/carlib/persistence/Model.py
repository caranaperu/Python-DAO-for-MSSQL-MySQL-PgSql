"""Define la base para todos los modelos , esta clase es abstracta."""
from abc import ABCMeta, abstractmethod
from carlib.utils import cls_locked_attrs


#@cls_locked_attrs
class Model(object):
    """
    Clase base para todos los modelos.

    Esta clase debera ser usada como base a todas las demas que definan modelo, basicamente
    define los metodos basicos a implementar para interactura con las clases de manejo de
    persistencia.

    Example:
        class MyTestModel(BaseModel):
        def __init__(self):
            BaseModel.__init__(self)
            self.testfield = None
            self.modelo = None
            self.version = None
            self.marca = None

        def get_pk_fields(self):
            return ('marca','modelo')

        modelo = MyTestModel()

        record_values = {'version': 'HIGH ROOF A/C 2KD', 'modelo': 'HIACE', 'marca': 'TOYOTA','testfield':'Soy Test'}
        modelo.set_values(record_values)
        print(modelo.__dict__)
        print(modelo.get_pk_fields())

    """

    __metaclass__ = ABCMeta

    def set_values(self, record):
        """
        Setea los valores de los campos del modelo.

        Se entiende que los campos indicados en record deben corresponder a los campos del modelo,
        los que no correspondan seran ignorados.

        Parameters
        ----------
        record: dict of (str,Any)
            Diccionario conteniendo los campos y valores a asignar al modelo, lo campos deben
            corresponder a los atributos del modelo.

        Returns
        -------
            None

        Raises
        ------
        TypeError
            Si el parametro record no es un diccionario.

        """
        if isinstance(record, dict):
            for field, value in record.items():
                if hasattr(self, field):
                    setattr(self, field, value)
        else:
            raise TypeError(
                'record parameter need to be a dictionary of column names and values')

    def set_value(self, field, value):
        """
        Setea el valores de un campo del modelo.

        Parameters
        ----------
        field: str
            Con el nombre del campo del modelo a setear.
        value: Any
            El valor del campo indicado por field.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            Si el parametro field no esta definido.

        """
        if field is not None:
            if hasattr(self, field):
                setattr(self, field, value)
        else:
            raise ValueError('field parameter cant be None')

    @abstractmethod
    def get_pk_fields(self):
        """
        Retorna la lista de nombres de campos que componen la llave unica.

        Este metodo debera ser override para darle funcionalidad o debera simplemente
        retornar None en el caso que el metodo is_UID_pk retorna True.

        Returns
        -------
        tuple of (str)
            Con la lista de nombres de campos

        """
        pass

    def is_pk_uid(self):
        """
        Retorna si el modelo es identificado en forma unica por un UID.

        En el caso que este sea False , get_pk_fields debera estar definido.

        Returns
        -------
        bool
            True si el modelo es identificado por un UID.

        """
        return False

    def get_version_field(self):
        """
        Retorna el campo que indica la version del registro de existir uno.

        Returns
        -------
        str
            Nombre del campo distinto de None de existir uno. Por default devolvemos
            None.

        """
        return None
