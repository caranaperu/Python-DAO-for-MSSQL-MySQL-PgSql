from collections import OrderedDict

from enum import Enum
from copy import deepcopy


class Constraints(object):
    """
    Clase para los constraints de un query a la persistencia.

    Almacena los datos necesarios para acotar las clausulas sort y where y el inicio y fin a partir
    de donde se recogeran datos.

    Example:
        constraints = Constraints()

        constraints.offset = 100
        constraints.limit = 500

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

    class CallerOperation(Enum):
        """Enumeracion con las operaciones validas a asignar caller params."""

        ADD = 'add'
        DEL = 'del'
        FETCH = 'fetch'
        UPD = 'upd'
        READ = 'read'

    def __init__(self):
        """
        Inicializa variables.

        Todas las variables son inicializadas a None ya que solo seran accesadas via
        metodos (accesors)
        """
        self.__offset = None
        self.__limit = None
        # Privates
        self.__sort_fields = None
        self.__filter_fields = None
        self.__filter_fields_values = None
        self.__caller_params = None

    @property
    def offset(self):
        """
        Retorna a partir de que registro se leera en un query.

        Returns
        -------
        int
            El valor o None si no esta definido.

        """
        return self.__offset

    @offset.setter
    def offset(self, value):
        """
        Metodo que setea el campo privado offset.

        Si offset es mayor que limit no debera limitarse el numero de registros.

        Parameters
        ----------
        value: int
            Valor que indica a  partir de que registro se leera en un query.

        Returns
        -------
        None

        """
        if isinstance(value, int) is True:
            self.__offset = value
        else:
            self.__offset = None

    @property
    def limit(self):
        """
        Retorna a partir de que registro se leera en un query.

        Returns
        -------
        int
            El valor o None si no esta definido.

        """
        return self.__limit

    @limit.setter
    def limit(self, value):
        """
        Metodo que setea el campo privado limit.

        Si offset es mayor que limit no debera limitarse el numero de registros.

        Parameters
        ----------
        value: int
            Valor que indica hasta que registro se leera en un query.

        Returns
        -------
        None

        """
        if isinstance(value, int) is True:
            self.__limit = value
        else:
            self.__limit = None

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
        TypeError
            Si el parametro sort_field no es un string.
            Si el parametro sort_direction no es parte del enum DAOConstraints.SortType

        """
        # Si no existe creado el diccionario __sort_fields se crea.
        if self.__sort_fields is None:
            self.__sort_fields = OrderedDict()

        if sort_field is not None and (type(sort_field).__name__ == "str" or type(sort_field).__name__ == "unicode"):
            if type(sort_direction).__name__ == "SortType":
                self.__sort_fields[sort_field] = sort_direction.value
            else:
                raise TypeError(
                    '{0} is not a valid sort type'.format(sort_direction))
        else:
            raise TypeError(
                'The sort field ({0}) is not a string'.format(sort_field))

    def clear_sort_fields(self):
        """
        Limpia la lista de sort fields.

        Returns
        -------
        None

        """
        self.__sort_fields = None

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
        if self.sort_field_exists(sort_key_name) is False:
            del self.__sort_fields[sort_key_name]

    def sort_field_exists(self, sort_key_name):
        """
        Indica si un sort field existe.

        Parameters
        ----------
        sort_key_name: str
            Nombre del campo de sort a buscar.

        Returns
        -------
        bool
            True si existe , False de lo contrario

        """
        if self.__sort_fields and self.__sort_fields.get(sort_key_name) is not None:
            return True
        return False

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

    def add_filter_field(self, field_name, field_value, filter_type):
        """
        Agrega un campo de filtro a los constraints indicando su valor y el tipo de filtro.

        Es importante saber que si el filter field ha agregar ya existe no se creara
        uno nuevo sino se reemplazara al existente con el nuevo valor y tipo de filtro..

        Parameters
        ----------
        field_name: str
            Nombre del campo de filtro a agregar al diccionario de campos de filtro.
        field_value: Any
            El valor del filtro a aplicar por ejemplo si el tipo de filtro es >= este
            valor podria ser un valor entero como 100.
        filter_type: Constraints.FilterType
            Indicara el tipo de filtro como mayor o igual, menor,igual , etc

        Returns
        -------
        None

        Raises
        ------
        TypeError
            Si el parametro field_name no es un string.
            Si el parametro filter_type no es parte del enum DAOConstraints.FilterType
            Si el parametro field_call_order no es entero

        """
        # Si no existe creado el diccionario __filter_fields se crea asi como el que
        # contiene los valores.
        if self.__filter_fields is None:
            self.__filter_fields = {}
            self.__filter_fields_values = {}

        if field_name is not None and type(field_name) is str:
            if type(filter_type).__name__ == "FilterType":
                self.__filter_fields[field_name] = filter_type
                self.__filter_fields_values[field_name] = field_value
            else:
                raise TypeError(
                    '{0} is not a valid filter type'.format(filter_type))
        else:
            raise TypeError(
                'The filter field ({0}) is not a string'.format(field_name))

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
        -------
        Any
            Con el valor del filtro o None si el filter_key_name no existe en la lista
            de filtros.`

        """
        if self.__filter_fields_values.get(filter_key_name) is not None:
            return self.__filter_fields_values[filter_key_name]
        return None

    def add_caller_parameter(self, operation, field_value, call_order=None):
        """
        Agrega un campo de que sera usado como parametro de entrada en el caso una operacion
        se soporte en un stored procedure.

        Es conveniente que el orden que se indique no se repita entre caller parameters, ya que
        de ser asi el orden de estos al ser colocados como parametros del sp sera indeterminado.

        Parameters
        ----------
        operation: Constraints.CallerOperation
            Indicara el tipo de operacion sobre el que tendra efecto este campo.
        field_value: Any
            El valor del filtro a aplicar por ejemplo si el tipo de filtro es >= este
            valor podria ser un valor entero como 100.
            IMPORTANTE: En el caso que la operacion tenga un modelo definido como en el caso
                        de add , update aqui podra indicarse el nombre del campo dentro del
                        modelo y se usara el modelo para extraer el valor del campo.
        call_order: int
            Si este campo sera usado como call parameter indicar aqui el orden.
            Si se indica el mismo orden en varios el orden al ser leido sera inesperado
            usese siempre valores distintos.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            Si el parametro operation no es parte del enum Constraints.CallerOperation
            Si el parametro call_order no es entero

        """
        # Si no existe creado el diccionario __filter_fields se crea asi como el que
        # contiene los valores.
        if type(operation).__name__ != "CallerOperation":
            raise TypeError(
                '{0} is not a valid operation'.format(operation))

        if type(call_order) != int:
            raise TypeError(
                'call_order parameter need to be an integer')

        if self.__caller_params is None:
            self.__caller_params = {}
        if self.__caller_params.get(operation.value) is None:
            self.__caller_params[operation.value] = []

        self.__caller_params[operation.value].append({'value': field_value, 'call_order': call_order})

    def get_caller_params(self, operation):
        """
        Retorna los parametros de stored procedure ordenados para una determinada operacion.

        Parameters
        ----------
        operation: Constraints.CallerOperation
            Indicara el tipo de operacion sobre el que tendra efecto este campo.

        Returns
        -------
        list of dict[any,int]

        """
        cparams = self.__caller_params[operation.value]
        return sorted(cparams, key=lambda t: t['call_order'])

    @property
    def caller_params(self):
        """
        Metodo property para evitar el acceso directo a la variable __caller_params

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Indicando el acceso no permitido a la variable

        """
        raise AttributeError(
            'not allowed direct access to caller params , use get_caller_params instead')
