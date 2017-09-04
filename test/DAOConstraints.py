from typing import List, Dict, Any
from enum import Enum
from copy import deepcopy


class DAOConstraints(object):
    """
    Clase para los constraints de un SQL query.

    Almacena los datos necesarios para acotar las clausulas sort
    y where y asi mismo tiene utilitarios para generar standar ANSI en dichas
    clausulas , la generacion de la clausula where tiene como limitacion que
    siempre seran todos AND o OR pero no combinados.
    """

    class SortType(Enum):
        """Enumeracion que contiene los tipos de sort."""

        ASC = "ASC"
        DESC = "DESC"

    class FilterType(Enum):
        """Enumeracion que contiene los tipos de operadores de filtros."""

        EQUAL = "="
        NO_EQUAL = "<>"
        PARTIAL = "like"
        IPARTIAL = "ilike"
        GREAT_THAN = ">"
        GREAT_THAN_EQ = ">="
        LESS_THAN = "<"
        LESS_THAN_EQ = "<="

    def __init__(self):
        # type: () -> None
        """Initialize constraint variables."""
        self.__start_row = None  # type: int
        self.__end_row = None  # type: int
        # Privates
        self.__sort_fields = None  # type: Dict[str,DAOConstraints.SortType]
        self.__filter_fields = None # type: Dict[str,DAOConstraints.FilterType]
        self.__filter_fields_values = None  # type: Dict[str,Any]

    @property
    def start_row(self):
        # type: () -> int
        """
        Retorna a partir de que registro se leera en un query.

        Util para general querys con un numero de limitado de
        registros a leer, este atributo funciona en conjunto con end_row.

        Si este atributo es None no debera limitara el numero de registros a leer
        en el query.

        Si start_row es mayor que end_row no se limitara el numero de registros.
        """
        print("Getting value")
        return self.__start_row

    @start_row.setter
    def start_row(self, value):
        # type: (int) -> None
        """
        Metodo que manipula el campo start_row.

        Seteara el valor siempre que value sea un entero , de no serlo sera None.
        """
        print("Setting value")
        if (isinstance(value, int) is True):
            self.__start_row = value
        else:
            self.__start_row = None

    @start_row.deleter
    def start_row(self):
        del self.__start_row

    @property
    def end_row(self):
        # type: () -> int
        """
        Retorna hasta que registro se leera en un query.

        Util para general querys con un numero de limitado de
        registros a leer, este atributo funciona en conjunto con start_row.

        Si este atributo es None no debera limitar hasta que numero de registro
        se leera en el query, si start_row es None se asumira todos ahasta el limite
        indicado por end_row.

        Si end_row es menor que start_row no se limitara el numero de registros.
        """
        print("Getting value")
        return self.__end_row

    @end_row.setter
    def end_row(self, value):
        # type: (int) -> None
        """
        Metodo que manipula el campo end_row.

        Seteara el valor siempre que value sea un entero , de no serlo sera None.
        """
        print("Setting value")
        if (isinstance(value, int) is True):
            self.__end_row = value
        else:
            self.__end_row = None

    @end_row.deleter
    def end_row(self):
        del self.__end_row

    @property
    def sort_fields(self):
        # type: () -> Dict[str,DAOConstraints.SortType]
        """Retorna un deepcopy del diccionario de campos de order by."""
        return deepcopy(self.__sort_fields)

    @sort_fields.deleter
    def sort_fields(self):
        del self.__sort_fields

    def add_sort_field(self, sort_field, sort_direction=SortType.ASC):
        # type: (str,DAOConstraints.SortType) -> None
        """
        Agrega un campo de sort a los constraints indicando la direccion.

        Es importante saber que si el sort field  ha agregar ya existe no se creara
        uno nuevo sino se reemplazara al existente con el nuevo sort type.

        El parametro sort_field debe ser un string de lo contrario se enviara una
        excepcion AttributeError.

        El parametro sort_direction debe ser del tipo SortType ya que de no ser asi
        ocurrira la excepcion  AttributeError.

        """
        # Si no existe creado el diccionario __sort_fields se crea.
        if (self.__sort_fields is None):
            self.__sort_fields = {}

        if (sort_field != None and type(sort_field).__name__ == "str"):
            if (type(sort_direction).__name__ == "SortType"):
                self.__sort_fields[sort_field] = sort_direction.value
            else:
                raise AttributeError(
                    '{0} is not a valid sort type'.format(sort_direction))
        else:
            raise AttributeError(
                'The sort field ({0}) is not a string'.format(sort_field))

    def del_sort_field(self, sort_key_name):
        # type: (str) -> None
        """Elimina un sort field DE EXISTIR."""
        if (self.__sort_fields.get(sort_key_name) != None):
            del self.__sort_fields[sort_key_name]

    @property
    def filter_fields(self):
        # type: () -> Dict[str,DAOConstraints.FilterType]
        """Retorna un deepcopy del diccionario de campos de filtro."""
        return deepcopy(self.__filter_fields)

    @filter_fields.deleter
    def filter_fields(self):
        del self.__filter_fields

    def add_filter_field(self, filter_field, filter_value, filter_type):
        # type: (str,Any,DAOConstraints.FilterType) -> None
        """
        Agrega un campo de filtro a los constraints indicando su valor y el tipo de filtro.

        Es importante saber que si el filter field ha agregar ya existe no se creara
        uno nuevo sino se reemplazara al existente con el nuevo valor y tipo de filtro..

        El parametro filter_field debe ser un string de lo contrario se enviara una
        excepcion AttributeError.

        El parametro filter_type debe ser del tipo FilterType ya que de no ser asi
        ocurrira la excepcion  AttributeError.

        """
        # Si no existe creado el diccionario __filter_fields se crea asi como el que
        # contiene los valores.
        if (self.__filter_fields is None):
            self.__filter_fields = {}
            self.__filter_fields_values = {}

        if (filter_field != None and type(filter_field).__name__ == "str"):
            if (type(filter_type).__name__ == "FilterType"):
                self.__filter_fields[filter_field] = filter_type
                self.__filter_fields_values[filter_field] = filter_value
            else:
                raise AttributeError(
                    '{0} is not a valid filter type'.format(filter_type))
        else:
            raise AttributeError(
                'The filter field ({0}) is not a string'.format(filter_field))

    def del_filter_field(self, filter_key_name):
        # type: (str) -> None
        """Elimina un filter field DE EXISTIR."""
        if (self.__filter_fields.get(filter_key_name) != None):
            del self.__filter_fields[filter_key_name]
            del self.__filter_fields_values[filter_key_name]

    def get_filter_field_value(self, filter_key_name):
        # type: (str) -> Any
        """
        Retorna el valor de un campo de filtro.

        Si no existe retornara None.
        """
        if (self.__filter_fields_values.get(filter_key_name)) != None:
            return self.__filter_fields_values[filter_key_name]
        return None



if __name__ == "__main__":

    daoc = DAOConstraints()
    daoc.start_row = 100
    daoc.end_row = 500
    print(daoc.start_row)
    print(daoc.end_row)
    daoc.end_row = None
    print(daoc.end_row)

    print(daoc.__dict__)

    print(type("ssss"))

    # daoc.add_sort_field('xxd', "dddd")
    daoc.add_sort_field('xxd1', DAOConstraints.SortType.DESC)
    daoc.add_sort_field('xxd', DAOConstraints.SortType.ASC)
    daoc.add_sort_field('ssss', DAOConstraints.SortType.ASC)
    daoc.add_sort_field('555', DAOConstraints.SortType.ASC)

    daoc.add_filter_field('field_1', 3, DAOConstraints.FilterType.EQUAL)
    daoc.add_filter_field('field_2', "soy el field1",
                          DAOConstraints.FilterType.EQUAL)

    daoc.add_filter_field(
        'fiel_3', 100.00, DAOConstraints.FilterType.GREAT_THAN)
    daoc.add_filter_field(
        'fiel_31', 100.00, DAOConstraints.FilterType.LESS_THAN_EQ)
    daoc.add_filter_field(
        'fiel_32', 100.00, DAOConstraints.FilterType.NO_EQUAL)

    daoc.add_filter_field('fiel_4', None, DAOConstraints.FilterType.NO_EQUAL)
    daoc.add_filter_field('fiel_5', None, DAOConstraints.FilterType.EQUAL)



    print(daoc.__dict__)
    daoc.del_sort_field('sas')
    print(daoc.__dict__)
    daoc.del_sort_field('xxd')
    print(daoc.__dict__)

    daoc.add_filter_field('ddddd', 3, DAOConstraints.FilterType.EQUAL)
    aa = daoc.get_filter_field_value('dddd')
    print(aa)

    aa = daoc.get_filter_field_value('ddddd')
    print(aa)
    print(daoc.__dict__)

    # daoc.add_filter_field('ddddd',45,"dddd")

    def memory_address(in_var):
        return hex(id(in_var))

    def test():
        a = ['test', 'xxxx']
        print(memory_address(a))
        return a

    print("-----1")
    bxxx = test()
    print(bxxx)
    print(memory_address(bxxx))
    print("-----2")
    bxxx.append('DDDDD')
    print(memory_address(bxxx))

    print("-----3")
    print(bxxx)
    print(memory_address(bxxx))

    print("-----4")
    cxxx = test()
    print(memory_address(cxxx))
    print(memory_address(cxxx[0]))
    xxxx = test()
    print(memory_address(xxxx))
    print(memory_address(xxxx[0]))
    cxxx.append('ddddd')
    print(memory_address(cxxx))
    print(memory_address(cxxx[0]))

    print(cxxx)
    print(xxxx)

    print("---------------------------------------------")
    print(test())




