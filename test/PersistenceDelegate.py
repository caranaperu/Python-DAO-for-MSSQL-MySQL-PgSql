from abc import ABCMeta, abstractmethod
from copy import deepcopy


class PersistenceDelegate(object):
    """Clase abstracta que define metodos para efectuar operaciones en la persistencia."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Inicializa variables con defaults.

        Estas seran seteadas via accesor o metodos al sobrescribirse esta clase.

        """
        self.__add_def = None
        self.__read_def = None
        self.__update_def = None
        self.__delete_def = None
        self.__fetch_def = None

    @property
    def add_definition(self):
        """
        Retorna la definicion para add.

        Returns
        -------
        dict[str,any]
            La definicio para add.

        """
        return self.__add_def

    @add_definition.setter
    def add_definition(self, def_values):
        """
        Setea la definicion para un add a la persistencia.

        Por default crea un deepcopy del diccionario enviado por def_values, siempre
        que este este definido y sea del tipo correcto.

        Parameters
        ----------
        def_values: dict[str,any]
            Este diccionario contendra la definicion de valores que puedan requerirse para efectuar
            un add a la persistencia , la interpretacion sera valida por las clases que sobrescriban
            esta.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro def_values no es un diccionario.

        """
        if def_values and isinstance(def_values, dict):
            self.__add_def = deepcopy(def_values)
        else:
            raise AttributeError(
                'def_values parameter is not a dictionary')

    @property
    def read_definition(self):
        """
        Retorna la definicion para read.

        Returns
        -------
        dict[str,any]
            La definicio para read.

        """
        return self.__read_def

    @read_definition.setter
    def read_definition(self, def_values):
        """
        Setea la definicion para la lectura de un registro a la persistencia.

        Por default crea un deepcopy del diccionario enviado por def_values.

        Parameters
        ----------
        def_values: dict[str,any]
            Este diccionario contendra la definicion de valores que puedan requerirse para efectuar
            una lectura a la persistencia , la interpretacion sera valida por las clases que
            sobrescriban esta.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro def_values no es un diccionario.

        """
        if def_values and isinstance(def_values, dict):
            self.__read_def = deepcopy(def_values)
        else:
            raise AttributeError(
                'def_values parameter is not a dictionary')

    @property
    def update_definition(self):
        """
        Retorna la definicion para update.

        Returns
        -------
        dict[str,any]
            La definicio para update.

        """
        return self.__update_def

    @update_definition.setter
    def update_definition(self, def_values):
        """
        Setea la definicion para un update a la persistencia.

        Por default crea un deepcopy del diccionario enviado por def_values, siempre
        que este este definido y sea del tipo correcto.

        Parameters
        ----------
        def_values: dict[str,any]
            Este diccionario contendra la definicion de valores que puedan requerirse para efectuar
            un update a la persistencia , la interpretacion sera valida por las clases que sobrescriban
            esta.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro def_values no es un diccionario.

        """
        if def_values and isinstance(def_values, dict):
            self.__update_def = deepcopy(def_values)
        else:
            raise AttributeError(
                'def_values parameter is not a dictionary')

    @property
    def delete_definition(self):
        """
        Retorna la definicion para delete.

        Returns
        -------
        dict[str,any]
            La definicio para delete.

        """
        return self.__delete_def

    @delete_definition.setter
    def delete_definition(self, def_values):
        """
        Setea la definicion para un delete a la persistencia.

        Por default crea un deepcopy del diccionario enviado por def_values, siempre
        que este este definido y sea del tipo correcto.

        Parameters
        ----------
        def_values: dict[str,any]
            Este diccionario contendra la definicion de valores que puedan requerirse para efectuar
            un delete a la persistencia , la interpretacion sera valida por las clases que sobrescriban
            esta.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro def_values no es un diccionario.

        """
        if def_values and isinstance(def_values, dict):
            self.__delete_def = deepcopy(def_values)
        else:
            raise AttributeError(
                'def_values parameter is not a dictionary')

    @property
    def fetch_definition(self):
        """
        Retorna la definicion para fetch.

        Returns
        -------
        dict[str,any]
            La definicio para fetch.

        """
        return self.__fetch_def

    @fetch_definition.setter
    def fetch_definition(self, def_values):
        """
        Setea la definicion para un fetch a la persistencia.

        Por default crea un deepcopy del diccionario enviado por def_values, siempre
        que este este definido y sea del tipo correcto.

        Parameters
        ----------
        def_values: dict[str,any]
            Este diccionario contendra la definicion de valores que puedan requerirse para efectuar
            un fetch a la persistencia , la interpretacion sera valida por las clases que sobrescriban
            esta.

        Returns
        -------
        None

        Raises
        ------
        AttributeError
            Si el parametro def_values no es un diccionario.

        """
        if def_values and isinstance(def_values, dict):
            self.__fetch_def = deepcopy(def_values)
        else:
            raise AttributeError(
                'def_values parameter is not a dictionary')

    @abstractmethod
    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        """
        Retorna la definicion para la lectura de un registro en la persistencia.

        Parameters
        ----------
        record_model: Model
            Modelo el cual si pk_keys define una lista de campos , entonces este modelo contendra
            los valores de dichos campos.
        key_values: int or tuple[str]
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, opcional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con un string representando la sentencia a ejecutar, tal como la entienda la
            persistencia.

        """
        pass

    @abstractmethod
    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):
        """
        Retorna la definicion para la lectura de multiples registros en la persistencia.

        Para efectuar las limitaciones de esta busqueda se usaran los constraints.

        Parameters
        ----------
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener los registros.
        sub_operation: str, opcional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con un string representando la sentencia a ejecutar, tal como la entienda la
            persistencia.

        """
        pass

    @abstractmethod
    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        """
        Retorna la definicion para agregar un registro a la persistencia.

        Parameters
        ----------
        record_model: Model
            El modelo de datos con los datos del registro a agregar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con un string representando la sentencia a ejecutar, tal como la entienda la
            persistencia.

        """
        pass

    @abstractmethod
    def get_update_record_query(self, record_model, sub_operation=None):
        """
        Retorna la definicion para efectuar un update a un registro a la persistencia.

        Parameters
        ----------
        record_model: Model
            El modelo de datos con los datos del registro a actualizar.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con un string representando la sentencia a ejecutar, tal como la entienda la
            persistencia.

        """
        pass

    @abstractmethod
    def get_delete_record_query(self, key_values):
        """
        Retorna la definicion para efectuar un delete a un registro a la persistencia.

        Parameters
        ----------
        key_values: int or tuple[any]
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.

        Returns
        -------
        str
            Con un string representando la sentencia a ejecutar, tal como la entienda la
            persistencia.

        """
        pass

    def execute_fetch(self, handler, c_constraints=None, sub_operation=None, raw_answers=True, record_type_classname=None):
        """
        Ejecuta la lectura de multiples registros a la base de datos.

        Este metodo llamara a callproc o execute sobre el cursor dependiendo de lo configurado
        en __fetch_def.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener los registros.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        raw_answers: bool
            Si se desea que la respuesta sea exactamente la devuelta por el driver y no una lista
            de modelos.
        record_type_classname: type Model , optional
            El type de la clase del modelo a usar si se requiere que se retorna una listqa de modelos
            como respuesta.
            Si raw_answers es False este parametro es obligatorio.

        Returns
        -------
        list[tuple[any]] or list[tuple[Model]]
            la lista de resultados si raw_answers es True o una lista de Modelos
            si raw_answers es False

        Raises
        ------
        PersistenceException
            El  motivo de la excepcion se encuentra en e.persistent_error y puede ser cualquiera
            de los siguientes:
                DB_ERR_SERVERNOTFOUND , si no hay posibilidad de conectarse a la persistencia.
                DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
                DB_ERR_ALLOK          , Lectura correcta.

        """
        pass

    def execute_add(self, handler, record_model, c_constraints=None, sub_operation=None):
        """
        Ejecuta el agregar un registro a la base de datos.

        Este metodo llamara a callproc o execute sobre el cursor dependiendo de lo configurado
        en __add_def. No envia directamente una excepcion pero obviamente cualquier error en la
        operacion de la base de datos tendra que ser capturado por el metodo que invoca.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.
        record_model: Model
            El modelo de datos con los datos del registro a agregar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con la sentencia recien ejecutada.

        """
        pass

    def execute_read(self, handler, record_model, key_values, c_constraints=None, sub_operation=None):
        """
        Metodo el cual sera implementado para agregar un registro a la persistencia.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.
        record_model: Model
            El modelo de datos donde se colocaran los datos leidos.
        key_values: int or tuple[str]
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con la sentencia recien ejecutada.

        """
        pass

    def execute_update(self, handler, record_model, sub_operation=None):
        """
        Metodo el cual sera implementado para actualizar un registro a la persistencia.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.
        record_model: Model
            El modelo de datos con los datos del registro a agregar.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con la sentencia recien ejecutada.

        """
        pass

    def execute_delete(self, handler, key_values):
        """
        Metodo el cual sera implementado para eliminar un registro a la persistencia.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.
        key_values: int or tuple[str]
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.

        Returns
        -------
        str
            Con la sentencia recien ejecutada.

        """
        pass

    @abstractmethod
    def get_uid(self, handler):
        """
        Metodo el cual sera implementado para retornar el id unico del registro.

        Este unique identifier podria existir o no , ya que un registo puede tambien
        ser identificado por multiples campos normales.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.

        Returns
        -------
        int
            El unique id o None de no existir.

        """
        pass

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

    def is_record_modified_error(self, error_msg):
        """
        Metodo a implementar para indicar si un registro al hacer update o delete ha sido modificado
        externamente.

        Dado que la especificacion de los drivers de persistencia existentes no tienen una manera
        standard de codigos de error comun para casos como este , se espera que a traves
        del mensaje pueda determinarse si ese es el caso.

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usaso para desambiguar si es un error de registro modificado o no.

        Returns
        -------
        bool
            True si es un error de registro modificado , False de lo contrario.
            Si no es overriden retorna False por default.

        """
        return False
