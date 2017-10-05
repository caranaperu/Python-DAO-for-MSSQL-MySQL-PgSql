from abc import ABCMeta
from PersistenceDelegate import PersistenceDelegate


class DatabaseDelegate(PersistenceDelegate):
    """Clase abstracta que ejecuta las operaciones especificas sobre la base de datos."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Inicializa variables con defaults , estas seran seteadas via accesor o metodos.

        """
        PersistenceDelegate.__init__(self)
        self.add_definition = {'is_call': False, 'call_parameters': None}
        self.read_definition = {'is_call': False, 'call_parameters': None}
        self.update_definition = {'is_call': False, 'call_parameters': None}

    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        """
        Retorna la definicion del sql query para la lectura de un registro a la base de datos.

        Parameters
        ----------
        record_model: Model
            Modelo el cual si pk_keys define una lista de campos , entonces este modelo contendra
            los valores de dichos campos.
        key_values: int or tuple of str
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
            Con un string representando la sentencia sql a ejecutar, por default retorna None para
            evitar tener sobreescribir el metodo si no se realizara operacion de leer un registro.

        """
        return None

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        """
        Retorna la definicion del sql query para agregar un registro a la base de datos.

        Parameters
        ----------
        record_model: Model
            El modelo con los datos del registro a agregar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.

        Returns
        -------
        str
            Con un string representando la sentencia sql a ejecutar, por default retorna None para
            evitar tener sobreescribir el metodo si no se realizara operacion de add.

        """
        return None

    def get_update_record_query(self, record_model, sub_operation=None):
        """
        Retorna la definicion del sql query para efectuar un update a un registro a la
        base de datos.

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
            Con un string representando la sentencia sql a ejecutar, por default retorna None para
            evitar tener sobreescribir el metodo si no se realizara operacion de update.
        """
        return None

    def get_delete_record_query(self, key_values):
        """
        Retorna la definicion para efectuar un delete a un registro de la base de datos.

        Parameters
        ----------
        key_values: int or tuple of str
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.

        Returns
        -------
        str
            Con un string representando la sentencia a ejecutar, tal como la entienda la
            persistencia.

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
        handler: Cursor
            cursor de la base de datos sobre una coneccion abierta y con la cual se realizara la
            operacion.
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
            Con la sentencia sql recien ejecutada.

        """
        sql_sentence = self.get_add_record_query(
            record_model, c_constraints, sub_operation)
        add_def = self.add_definition
        if add_def['is_call']:
            if add_def['call_parameters']:
                params = []
                for field in add_def['call_parameters']:
                    # Si el parametro corresponde a un atrributo del
                    # modelo , se toma el valor del atributo , de lo contrario
                    # se asume como un parametro directo
                    if hasattr(record_model, field):
                        params.append(getattr(record_model, field))
                    else:
                        params.append(field)
                handler.callproc(sql_sentence, params)
            else:
                handler.callproc(sql_sentence)
        else:
            handler.execute(sql_sentence)
        return sql_sentence

    def execute_read(self, handler, record_model, key_values, c_constraints=None, sub_operation=None):
        """
        Ejecuta el agregar un registro a la base de datos.

        Este metodo llamara a callproc o execute sobre el cursor dependiendo de lo configurado
        en __add_def. No envia directamente una excepcion pero obviamente cualquier error en la
        operacion de la base de datos tendra que ser capturado por el metodo que invoca.

        Parameters
        ----------
        handler: Cursor
            cursor de la base de datos sobre una coneccion abierta y con la cual se realizara la
            operacion.
        record_model: Model
            El modelo de datos donde se colocaran los datos leidos. None si los key_values
            contienen valores directos no mapeados a campos.
        key_values: int or tuple of str
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
            Con la sentencia sql recien ejecutada.

        """
        sql_sentence = self.get_read_record_query(record_model, key_values, c_constraints, sub_operation)
        read_def = self.read_definition

        if read_def['is_call']:
            if read_def['call_parameters']:
                params = []
                for field in read_def['call_parameters']:
                    # Si el parametro corresponde a un atrributo del
                    # modelo , se toma el valor del atributo , de lo contrario
                    # se asume como un parametro directo
                    # En este caso si el modelo es None se asumira que
                    # los key_values contienen valores.
                    if record_model and hasattr(record_model, field):
                        params.append(getattr(record_model, field))
                    else:
                        params.append(field)
                handler.callproc(sql_sentence, params)
            else:
                handler.callproc(sql_sentence)
        else:
            handler.execute(sql_sentence)
        return sql_sentence

    def execute_update(self, handler, record_model, sub_operation=None):
        """
        Ejecuta el update a  un registro a la base de datos.

        Este metodo llamara a callproc o execute sobre el cursor dependiendo de lo configurado
        en __update_def. No envia directamente una excepcion pero obviamente cualquier error en la
        operacion de la base de datos tendra que ser capturado por el metodo que invoca.

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
        sql_sentence = self.get_update_record_query(record_model, sub_operation)
        update_def = self.update_definition

        if update_def['is_call']:
            if update_def['call_parameters']:
                params = []
                for field in update_def['call_parameters']:
                    # Si el parametro corresponde a un atrributo del
                    # modelo , se toma el valor del atributo , de lo contrario
                    # se asume como un parametro directo
                    if hasattr(record_model, field):
                        params.append(getattr(record_model, field))
                    else:
                        params.append(field)
                handler.callproc(sql_sentence, params)
            else:
                handler.callproc(sql_sentence)
        else:
            handler.execute(sql_sentence)
        return sql_sentence

    def execute_delete(self, handler, key_values):
        """
        Metodo el cual sera implementado para eliminar un registro a la persistencia.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.
        key_values: int or tuple of str
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.

        Returns
        -------
        str
            Con la sentencia recien ejecutada.

        """
        sql_sentence = self.get_delete_record_query(key_values)
        delete_def = self.update_definition

        if delete_def['is_call']:
            if delete_def['call_parameters']:
                params = []
                for field_value in delete_def['call_parameters']:
                    # Para este caso siempre seran valores directos
                    # ya que no existe modelo
                    params.append(field_value)
                handler.callproc(sql_sentence, params)
            else:
                handler.callproc(sql_sentence)
        else:
            handler.execute(sql_sentence)
        return sql_sentence
