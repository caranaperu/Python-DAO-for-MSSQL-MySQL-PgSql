
from abc import ABCMeta, abstractmethod


class PersistenceOperations(object):
    """Clase abstracta define las operaciones validas para accesar a la persistencia."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def read_record(self, key_values, record_model, c_constraints=None, sub_operation=None):
        """
        Metodo el cual sera implementado para la lectura de un registro en la persistencia.

        Parameters
        ----------
        key_values: int or tuple of str
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.
        record_model: Model
            El modelo de datos destino de los datos obtenidos.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, opcional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_RECORDNOTFOUND , si el registro no existe en la persistencia.
            DB_ERR_TOOMANYRESULTS , si existe mas de una respuesta para el key_value.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_ALLOK          , Lectura correcta , los valores leidos estaran en record_model.

        """
        pass

    @abstractmethod
    def add_record(self, record_model, c_constraints=None, sub_operation=None, reread_record=True):
        """
        Metodo el cual sera implementado para agregar un registro en la persistencia.

        Parameters
        ----------
        record_model: Model
            El modelo de datos conteniendo los datos a agregar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str , optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        reread_record: bool , default True
            Si es true , se releera el registro luego de agregarse , esto sera necesario si
            existen campos en el registro que se generan en la persistencia y no del lado del
            usuario.

        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , Si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_RECORDEXIST    , Si el registro ya existe en la persistencia.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_FOREIGNKEY     , Si el registro referencia a otro elemento no existente.
            DB_ERR_ALLOK          , Agregado correctamente.

        """
        pass

    @abstractmethod
    def update_record(self, record_model, sub_operation=None):
        """
        Metodo el cual sera implementado para actualizar un registro en la persistencia.

        Parameters
        ----------
        record_model: Model
            El modelo de datos conteniendo los datos a actualizar.
        sub_operation: str , optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , Si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_FOREIGNKEY     , Si el registro referencia a otro elemento no existente.
            DB_ERR_DUPLICATEKEY   , Si ya existe un registro con las mismas llaves unicas.
            DB_ERR_RECORD_MODIFIED,
            DB_ERR_ALLOK          , Actualizacion correcta.

        """
        pass

    @abstractmethod
    def delete_record(self, key_values, record_version_id=None, verified_delete_check=True):
        """
        Metodo el cual sera implementado para la eliminacion de un registro en la persistencia.

        Parameters
        ----------
        key_values: int or tuple of str
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.
        record_version_id: int
            Si el registro tiene un campo que indica la version del mismo , este parametro podra
            contener dicho valor si se requiere previamente comparar antes de eliminar si ha habido
            cambios en el registro.
        verified_delete_check: bool , default True
            Si es true , se verificara que la version del registro no haya cambiado antes de
            eliminarse.

        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , Si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_RECORDNOTFOUND , Si el registro no existe en la persistencia.
            DB_ERR_FOREIGNKEY     , Si el registro es referenciado por otro elemento en la persistencia.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_ALLOK          , Eliminacion correcta.

        """
        pass

    @abstractmethod
    def get_uid(self, cursor):
        """
        Metodo el cual sera implementado para retornar el id unico del registro.

        Este unique identifier podria existir o no , ya que un registo puede tambien
        ser identificado por multiples campos normales.

        Parameters
        ----------
        cursor: Cursor
            El cursor sobre el cual se esta ejecutando la poeracion a la persistencia.

        Returns
        -------
        int
            El unique id o None de no existir.

        """
        pass

    """
    Helpers para que en forma especifica se indique si el error en una determianda
    base de datos o persistencia corresponde a ciertos casos excepcionales , como llave
    duplicada o foreign key error u otros.
    Dado que el dbapi 2.0 no indica con claridad que contiene una excepcion , digase el
    codigo de error , pero si se garantiza por parte de las persistencias que el mensaje
    de error es unico en vada uno de los casos , enviamos el mensaje de la excepcion para
    se parsee y se determine si existe el error.
    """
    @abstractmethod
    def is_duplicate_key_error(self, error_msg):
        """
        Metodo a implementar para indicar si el error corresponde a llave duplicada.

        Dado que la especificacion de los drivers de persistencia existentes no tienen una manera
        standard de codigos de error comun para casos como llave duplicada , se espera que a traves
        del mensaje pueda determinarse si ese es el caso.

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usaso para desambiguar si es un error de llave duplicada o no.

        Returns
        -------
        bool
            True si es un error de llave duplicada , False de lo contrario.

        """
        pass

    @abstractmethod
    def is_foreign_key_error(self, error_msg):
        """
        Metodo a implementar para indicar si el error corresponde a foreign key.

        Dado que la especificacion de los drivers de persistencia existentes no tienen una manera
        standard de codigos de error comun para casos como foreign key , se espera que a traves
        del mensaje pueda determinarse si ese es el caso.

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usaso para desambiguar si es un error de foreign key o no.

        Returns
        -------
        bool
            True si es un error de foreign key , False de lo contrario.

        """
        pass
