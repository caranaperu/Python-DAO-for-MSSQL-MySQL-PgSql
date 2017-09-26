from enum import Enum
from copy import deepcopy


class Constraints(object):
    """
    Clase para los constraints de un query a la persistencia.

    Almacena los datos necesarios para acotar las clausulas sort y where y el inicio y fin a partir
    de donde se recogeran datos.

    Example:
        constraints = Constraints()

        constraints.start_row = 100
        constraints.end_row = 500

        constraints.add_sort_field('field_0', Constraints.SortType.DESC)
        constraints.add_sort_field('field_1', Constraints.SortType.ASC)

        constraints.add_filter_field('field_3', 100.00, Constraints.FilterType.GREAT_THAN)
        constraints.add_filter_field('field_3', 200.00, Constraints.FilterType.LESS_THAN_EQ)

        print(constraints.__dict__)

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
        """
        Inicializa variables.

        Todas las variables son inicializadas a None ya que solo seran accesadas via
        metodos (accesors)
        """
        self.__start_row = None
        self.__end_row = None
        # Privates
        self.__sort_fields = None
        self.__filter_fields = None
        self.__filter_fields_values = None

    @property
    def start_row(self):
        """
        Retorna a partir de que registro se leera en un query.

        Returns
        -------
        int
            El valor o None si no esta definido.

        """
        return self.__start_row

    @start_row.setter
    def start_row(self, value):
        """
        Metodo que setea el campo privado start_row.

        Si start_row es mayor que end_row no debera limitarse el numero de registros.

        Parameters
        ----------
        value: int
            Valor que indica a  partir de que registro se leera en un query.

        Returns
        -------
        None

        """
        if isinstance(value, int) is True:
            self.__start_row = value
        else:
            self.__start_row = None

    @start_row.deleter
    def start_row(self):
        del self.__start_row

    @property
    def end_row(self):
        """
        Retorna a partir de que registro se leera en un query.

        Returns
        -------
        int
            El valor o None si no esta definido.

        """
        return self.__end_row

    @end_row.setter
    def end_row(self, value):
        """
        Metodo que setea el campo privado end_row.

        Si start_row es mayor que end_row no debera limitarse el numero de registros.

        Parameters
        ----------
        value: int
            Valor que indica hasta que registro se leera en un query.

        Returns
        -------
        None

        """
        if isinstance(value, int) is True:
            self.__end_row = value
        else:
            self.__end_row = None

    @end_row.deleter
    def end_row(self):
        del self.__end_row

    @property
    def sort_fields(self):
        """
        Retorna un deepcopy del diccionario de campos de sort.

        Returns
        -------
        dict of (str,Constraints.SortType)
            deepcopy de los campos del sort en el constraint.

        """
        return deepcopy(self.__sort_fields)

    @sort_fields.deleter
    def sort_fields(self):
        del self.__sort_fields

    def add_sort_field(self, sort_field, sort_direction=SortType.ASC):
        """
        Agrega un campo de sort a los constraints indicando la direccion.

        Es importante saber que si el sort field  a agregar ya existe no se creara
        uno nuevo sino se reemplazara al existente con el nuevo sort type.

        Parameters
        ----------
        sort_field: str
            Nombre del campo de sort a agregar al diccionario de campos de sort.
        sort_direction: Constraints.SortType, default DAOConstraints.SortType.ASC
            Indicara si la direccion es ascendente o descendente para el sort.`

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro sort_field no es un string.
            Si el parametro sort_direction no es parte del enum DAOConstraints.SortType

        """
        # Si no existe creado el diccionario __sort_fields se crea.
        if self.__sort_fields is None:
            self.__sort_fields = {}

        if sort_field is not None and type(sort_field).__name__ == "str":
            if type(sort_direction).__name__ == "SortType":
                self.__sort_fields[sort_field] = sort_direction.value
            else:
                raise AttributeError(
                    '{0} is not a valid sort type'.format(sort_direction))
        else:
            raise AttributeError(
                'The sort field ({0}) is not a string'.format(sort_field))

    def del_sort_field(self, sort_key_name):
        """
        Elimina un sort field DE EXISTIR.

        Parameters
        ----------
        sort_key_name: str
            Nombre del campo de sort a eliminar del diccionario de campos de sort.

        Returns
        -------
        None

        """
        if self.__sort_fields.get(sort_key_name) is not None:
            del self.__sort_fields[sort_key_name]

    @property
    def filter_fields(self):
        """
        Retorna un deepcopy del diccionario de campos de filtro.

        Returns
        -------
        dict of (str,Constraints.FilterType)
            deepcopy de los campos de filtro en el constraint.

        """
        return deepcopy(self.__filter_fields)

    @filter_fields.deleter
    def filter_fields(self):
        del self.__filter_fields

    def add_filter_field(self, filter_field, filter_value, filter_type):
        """
        Agrega un campo de filtro a los constraints indicando su valor y el tipo de filtro.

        Es importante saber que si el filter field ha agregar ya existe no se creara
        uno nuevo sino se reemplazara al existente con el nuevo valor y tipo de filtro..

        Parameters
        ----------
        filter_field: str
            Nombre del campo de filtro a agregar al diccionario de campos de filtro.
        filter_value: Any
            El valor del filtro a aplicar por ejemplo si el tipo de filtro es >= este
            valor podria ser un valor entero como 100.
        filter_type: Constraints.FilterType
            Indicara el tipo de filtro como mayor o igual, menor,igual , etc

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro filter_field no es un string.
            Si el parametro filter_type no es parte del enum DAOConstraints.FilterType

        """
        # Si no existe creado el diccionario __filter_fields se crea asi como el que
        # contiene los valores.
        if self.__filter_fields is None:
            self.__filter_fields = {}
            self.__filter_fields_values = {}

        if filter_field is not None and type(filter_field).__name__ == "str":
            if type(filter_type).__name__ == "FilterType":
                self.__filter_fields[filter_field] = filter_type
                self.__filter_fields_values[filter_field] = filter_value
            else:
                raise AttributeError(
                    '{0} is not a valid filter type'.format(filter_type))
        else:
            raise AttributeError(
                'The filter field ({0}) is not a string'.format(filter_field))

    def del_filter_field(self, filter_key_name):
        """
        Elimina un filter field DE EXISTIR.

        Parameters
        ----------
        filter_key_name: str
            Nombre del campo de filtro del diccionario de campos de filtro.

        Returns
        -------
        None

        """
        if self.__filter_fields.get(filter_key_name) is not None:
            del self.__filter_fields[filter_key_name]
            del self.__filter_fields_values[filter_key_name]

    def get_filter_field_value(self, filter_key_name):
        """
        Retorna el valor de un campo de filtro.

        Parameters
        ----------
        filter_key_name: str
            Nombre del campo de filtro que deseamos buscar en la lista de filtros.

        Returns
        Any
            Con el valor del filtro o None si el filter_key_name no existe en la lista
            de filtros.`

        """
        if self.__filter_fields_values.get(filter_key_name) is not None:
            return self.__filter_fields_values[filter_key_name]
        return None
