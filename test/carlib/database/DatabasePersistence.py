import logging
from copy import deepcopy

from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabaseDelegate import DatabaseDelegate
from carlib.persistence.Model import Model
from carlib.persistence.PersistenceErrors import PersistenceErrors
from carlib.persistence.PersistenceOperations import *


class DatabasePersistence(PersistenceOperations):
    """
    Clase que efectua las operaciones CRUD a la base de datos sobre un determinado modelo y bajo
    una transaccion.

    Se soporta en un delegate para el caso de base de datos (DatabaseDelegate).

    Examples
    --------
        # Es pseudo code
        trx = TransactionManager('mssql', {'host': '192.168.0.9', 'port': '1433',
                                   'user': 'sa', 'password': 'melivane', 'database': 'pytest'})
        db_delegate = DatabaseDelegate()
        dao = DatabasePersistence(trx,db_delegate)

        ret = dao.add(someModel_1)

    """

    def __init__(self, trx_mgr, db_delegate):
        """
        Initialize  variables.

        Parameters
        ----------
        trx_mgr: TransactionManager
            Para el control de la transaccion , digase el commit o rollback segun sea necesario.
        db_delegate: DatabaseDelegate
            Para soporte de las operaciones CRUD especificas para base de datos.

        Raises
        ------
        ValueError
            En el caso que trx_mgr no sea instancia de TransactionManager
            En el caso que db_delegate no sea instancia de DatabaseDelegate
        """
        PersistenceOperations.__init__(self)

        # Debe estar definido el transaction manager , verificamos que
        # dicho parametro sea de la instancia correcta.
        if isinstance(trx_mgr, TransactionManager):
            self.__trx_mgr = trx_mgr  # type: TransactionManager
        else:
            raise ValueError(
                'trx_mgr parameter need to be an instance of TransactionManager')

        # El dao delegate es opcional , pero de estar definido debe ser del tipo
        # DatabaseDelegate.
        self.__db_delegate = None
        if db_delegate:
            if isinstance(db_delegate, DatabaseDelegate):
                self.__db_delegate = db_delegate
                # seteamos al delegate sobre que driver funciona
                self.__db_delegate.driver_id = self.__trx_mgr.db_driver_id
            else:
                raise ValueError(
                    'db_delegate parameter need to be an instance of DatabaseDelegate')
        else:
            raise ValueError('db_delegate need to be defined')

    def read_record(self, key_values, record_model, c_constraints=None, sub_operation=None):
        """
        Metodo para la lectura de un registro en la base de datos.

        En el caso se use stored procedures la implementacion default no usara los key_values
        y mas bien usara los constraints y los call parameters definidos en los mismos.

        Parameters
        ----------
        key_values: int or tuple[str] or None
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            nombre de los campos que componen la llave unica que identifica un registro.
            Sera None si se lee el registro via stored procedure ya que en ese caso se obtendran
            los call parameters de los constraints.
        record_model: Model
            El modelo de datos destino de los datos obtenidos, si es None la lectura solo servira como
            verificacion de existencia del registro.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener el registro.
        sub_operation: str, optional
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
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug("Error starting transaction reading record with key {} , exception message {} ".format(
                key_values, str(ex)))
            return PersistenceErrors.DB_ERR_SERVERNOTFOUND

        ret_value = None

        try:

            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()

            self.__db_delegate.execute_read(cursor, record_model, key_values, c_constraints, sub_operation)

            fields_description = None
            rows = None

            # Punto 1
            # Dado que el driver de mysql soportado y al hecho de un query via callproc
            # bajo ese driver reporta las respuestas de manera no standard a traves de
            # stored_results, verificamos si exsten respuestas en dicho lugar , de no
            # encontrar nada procedemos de la manera habitual.
            if hasattr(cursor, 'stored_results'):
                for result in cursor.stored_results():
                    rows = result.fetchall()
                    fields_description = result.description

            # Si no hay respuestas encontradas pasamos al metodo normal.
            if rows is None:
                rows = cursor.fetchall()
                fields_description = cursor.description

            # Usamos este metodo en este caso ya que algunos drivers no devuelven el
            # numero de filas afectadas en forma correcta.
            # Hay que aclarar que esperamos un solo registro de respuesta por ende no hay riesgo
            # en usar fetchall y al menos nos garantizara tener el numero correcto de respuestas.
            rowcount = 0
            if rows:
                rowcount = len(rows)

            # Dado que este metodo debe leer un solo registro , si el numero de respuestas
            # es 1 hacemos update al modelo con los valores del registro.
            # Si el numero de registros es cero se entiende que no existe.
            # Si el numero de registros es de mas de 1 se entiende que el query es incorrecto
            if rowcount == 1:
                encodetype = self.__trx_mgr.encoding()
                if encodetype:
                    columns = [i[0].encode(encodetype).rstrip('\x00') for i in fields_description]
                else:
                    columns = [i[0] for i in fields_description]

                for col in columns:
                    print(col)

                # Colocamos la respuesta en el modelo, si record_model
                # no es None
                if record_model:
                    record = dict(zip(columns, rows[0]))
                    record_model.set_values(record)

                ret_value = PersistenceErrors.DB_ERR_ALLOK
            elif rowcount == 0:
                ret_value = PersistenceErrors.DB_ERR_RECORDNOTFOUND
            else:
                sql = self.__db_delegate.get_read_record_query(record_model, key_values, c_constraints, sub_operation)
                logging.debug(
                    "Too many records {} results for read a record with query - {}".format(rowcount, sql))
                ret_value = PersistenceErrors.DB_ERR_TOOMANYRESULTS
        except Exception as ex:
            sql = self.__db_delegate.get_read_record_query(record_model, key_values, c_constraints, sub_operation)
            logging.debug("Error reading record with key {} , exception message {}, sql = '{}'".format(
                key_values, str(ex), sql))
            ret_value = PersistenceErrors.DB_ERR_CANTEXECUTE
        finally:
            # Si no es un error terminal cerramos normalmente de lo contrario indicamos
            # que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            if ret_value != PersistenceErrors.DB_ERR_ALLOK and ret_value != PersistenceErrors.DB_ERR_RECORDNOTFOUND:
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()
        return ret_value

    def add_record(self, record_model, c_constraints=None, sub_operation=None, reread_record=True):
        """
        Metodo para agregar un registro en la base de datos.

        Parameters
        ----------
        record_model: Model
            El modelo de datos conteniendo los datos a agregar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para agregar el registro.
            Basicamente sera usado si el add es realizado via stored procedure y se tomaran los
            caller parameters desde los mismos.
        sub_operation: str , optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        reread_record: bool
            Si es true , se releera el registro luego de agregarse , esto sera necesario si
            existen campos en el registro que se generan en la persistencia y no del lado del
            usuario. (default is True)

        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , Si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_RECORDEXIST    , Si el registro ya existe en la persistencia.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_FOREIGNKEY     , Si el registro referencia a otro elemento no existente.
            DB_ERR_ALLOK          , Agregado correctamente.

        """
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug(
                "Error starting transaction adding a record , exception message {} ".format(str(ex)))
            return PersistenceErrors.DB_ERR_SERVERNOTFOUND

        ret_value = None

        try:
            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()

            # add record
            self.__db_delegate.execute_add(cursor, record_model, c_constraints, sub_operation)

            # Si hay que reller el registro agregado , debemos u obteber el uid o las keys
            # unicas que identifican un registro.
            if reread_record:
                # Si el modelo no es identificado por un uid , solicitamos a este
                # cuales son los campos que contienen la llave unica.
                if not record_model.is_pk_uid():
                    pk_keys = record_model.get_pk_fields()
                else:
                    pk_keys = self.get_uid(cursor)

                # relectura.
                ret_value = self.read_record(
                    pk_keys, record_model, c_constraints, sub_operation)
            else:
                ret_value = PersistenceErrors.DB_ERR_ALLOK
        except Exception as ex:
            sql = self.__db_delegate.get_add_record_query(record_model, c_constraints, sub_operation)

            if self.is_duplicate_key_error(str(ex)):
                logging.debug(
                    "Error adding record , ya existe un registro con la misma llave,sql = '{}'".format(sql))
                ret_value = PersistenceErrors.DB_ERR_RECORDEXIST
            elif self.is_foreign_key_error(str(ex)):
                logging.debug(
                    "Error adding record , foreign key error,sql = '{}'".format(sql))
                ret_value = PersistenceErrors.DB_ERR_FOREIGNKEY
            else:
                logging.debug(
                    "Error adding record , exception message {} , sql ='{}'".format(str(ex), sql))
                ret_value = PersistenceErrors.DB_ERR_CANTEXECUTE
        finally:
            # Si no es un error terminal cerramos normalmente de lo contrario indicamos
            # que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            if ret_value != PersistenceErrors.DB_ERR_ALLOK:
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()
        return ret_value

    def delete_record(self, key_values, verified_delete_check=True, c_constraints=None, sub_operation=None):
        """
        Metodo para la eliminacion de un registro en la base de datos.

        Si usa para eliminar un stored procedure y verified_delete_check es True tanto los
        key_values como los caller params constraints DEBEN SER IGUALES, si verified_delete_check
        es False los ke_values son irrelevantes.

        Parameters
        ----------
        key_values: int or tuple[any] or None
            Si es entero representara el unique id de lo contrario sera un tuple con la lista de
            de los valores de los campos que componen la llave unica que identifica un registro.
            Podra ser None si se usan los constraints.
        verified_delete_check: bool , default True
            Si es true , se verificara que la version del registro no haya cambiado antes de
            eliminarse.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para eliminar el registro.
            Basicamente seran tomados en la implementacion default solo en el caso que se elimine
            via stored procedure y se extraeran de alli los caller parameters.
            No seran opcionales si se indica verified_delete_check=True y la lectura del registro
            a eliminar sea un stored procedure.
        sub_operation: str , optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , Si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_RECORDNOTFOUND , Si el registro no existe en la persistencia.
            DB_ERR_FOREIGNKEY     , Si el registro es referenciado por otro elemento en la persistencia.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_ALLOK          , Eliminacion correcta.

        """
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug(
                "Error starting transaction updating a record , exception message {} ".format(str(ex)))
            return PersistenceErrors.DB_ERR_SERVERNOTFOUND

        ret_value = PersistenceErrors.DB_ERR_ALLOK

        try:
            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()

            # relectura.
            if verified_delete_check:
                ret_value = self.read_record(key_values, None, c_constraints)

            if ret_value == PersistenceErrors.DB_ERR_ALLOK:
                # delete record
                self.__db_delegate.execute_delete(cursor, key_values, c_constraints)
            else:
                return ret_value

        except Exception as ex:
            sql = self.__db_delegate.get_delete_record_query(key_values, c_constraints)

            if self.is_foreign_key_error(str(ex)):
                logging.debug(
                    "Error deleting record , foreign key error,sql = '{}'".format(sql))
                ret_value = PersistenceErrors.DB_ERR_FOREIGNKEY
            else:
                logging.debug(
                    "Error deleting record , exception message {} , sql ='{}'".format(str(ex), sql))
                ret_value = PersistenceErrors.DB_ERR_CANTEXECUTE
        finally:
            # Si no es un error terminal cerramos normalmente de lo contrario indicamos
            # que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            if ret_value != PersistenceErrors.DB_ERR_ALLOK:
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()
        return ret_value

    def update_record(self, record_model, sub_operation=None, c_constraints=None, reread_record=True):
        """
        Metodo para actualizar un registro en la base de datos.

        Hay que resaltar que ademas de efectuar el update , puede verificar si el registro
        ha sido modificado o eliminado antes de actualizar.
        Al terminar reelera el registro para obtener los datos que pueden ser modificados
        por triggers o stored procedures internos y mantener asi actualizado el modelo
        con todos los datos luego de la actualizacion.

        Para determinar si el registro ha sido modificado , el modelo debera implementar
        get_version_field() y retornar el nombre del campo para validar la version
        del registro , no existe forma standard de hacerlo , en pgsql por ejemplo xmin
        puede ser usado para esto , en otras bases puede ser un timestamp o rowversion.

        Si ademas se desea releer los datos al final usar el parametro reread_record.


        Parameters
        ----------
        record_model: Model
            El modelo de datos conteniendo los datos a actualizar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para actualizar el registro.
            Si el update es via stored procedure debera indicarse los parametros via los constraints
            y los correspondientes caller parameters.
        sub_operation: str , optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        reread_record: bool , default True
            Si es true , se releera el registro luego de actualizarse, esto sera necesario si
            existen campos en el registro que se generan en la persistencia y no del lado del
            usuario y se desea actualizar el modelo con todos los datos del registro actualizado.

        Returns
        -------
        PersistenceErrors
            DB_ERR_SERVERNOTFOUND , Si no hay posibilidad de conectarse a la persistencia.
            DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
            DB_ERR_FOREIGNKEY     , Si el registro referencia a otro elemento no existente.
            DB_ERR_DUPLICATEKEY   , Si ya existe un registro con las mismas llaves unicas.
            DB_ERR_RECORD_MODIFIED, Si se detecta que antes de update el registro ha sido cambiado
                                    externamente. El modelo final  tendra los datos modificados.
            DB_ERR_RECORDNOTFOUND , Si ha sido eliminado externamente antes del update.
            DB_ERR_ALLOK          , Actualizacion correcta.

        """
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug(
                "Error starting transaction updating a record , exception message {} ".format(str(ex)))
            return PersistenceErrors.DB_ERR_SERVERNOTFOUND

        ret_value = PersistenceErrors.DB_ERR_ALLOK

        try:
            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()

            # Durante un update las unique keys se conocen desde el modelo
            # por ende solicitamos cuales son y en el caso sea un unique id
            # recogemos el valor como llave de lo contrario se espera la
            # lista de campos que identifican en forma unica el registro.
            pk_keys = record_model.get_pk_fields()

            # Si el unique id es el pk enviamos el valor, de lo contrario se enviaran
            # la lista de campos que hacen unico el registro.
            if pk_keys and record_model.is_pk_uid():
                pk_keys = getattr(record_model, pk_keys[0])

            # Extraempos del modelo enviado la version del registro , siempre
            # que el modelo soporte version.
            if record_model.get_version_field():
                version_field_upd = getattr(record_model, record_model.get_version_field())

                if version_field_upd:
                    # Copia para no alterar el original
                    record_model_to_read = deepcopy(record_model)
                    # lectura para verificacion de version
                    ret_value = self.read_record(pk_keys, record_model_to_read, c_constraints)

                    if ret_value == PersistenceErrors.DB_ERR_ALLOK:
                        # Comparamos la version original vs el recientemente leido
                        # de ser diferentes se indica el error de registro modificado.
                        version_field_read = getattr(record_model_to_read, record_model_to_read.get_version_field())
                        if str(version_field_upd) != str(version_field_read):
                            # Ponemos los datos modificados en el record model
                            record_model = deepcopy(record_model_to_read)
                            ret_value = PersistenceErrors.DB_ERR_RECORD_MODIFIED

            if ret_value == PersistenceErrors.DB_ERR_ALLOK:
                # update record
                self.__db_delegate.execute_update(cursor, record_model, c_constraints, sub_operation)

                # relectura.
                if reread_record:
                    ret_value = self.read_record(pk_keys, record_model, c_constraints, sub_operation)

        except Exception as ex:
            sql = self.__db_delegate.get_update_record_query(record_model, sub_operation)

            if self.is_duplicate_key_error(str(ex)):
                logging.debug(
                    "Error updating record , already exist a record with the key,sql = '{}'".format(sql))
                ret_value = PersistenceErrors.DB_ERR_RECORDEXIST
            elif self.is_foreign_key_error(str(ex)):
                logging.debug(
                    "Error updating record , foreign key error,sql = '{}'".format(sql))
                ret_value = PersistenceErrors.DB_ERR_FOREIGNKEY
            elif self.is_record_modified_error(str(ex)):
                logging.debug(
                    "Error updating record , record modified error,sql = '{}'".format(sql))
                ret_value = PersistenceErrors.DB_ERR_RECORD_MODIFIED
            else:
                logging.debug(
                    "Error updating record , exception message {} , sql ='{}'".format(str(ex), sql))
                ret_value = PersistenceErrors.DB_ERR_CANTEXECUTE
        finally:
            # Si no es un error terminal cerramos normalmente de lo contrario indicamos
            # que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            if ret_value != PersistenceErrors.DB_ERR_ALLOK:
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()
        return ret_value

    def fetch_records(self, c_constraints=None, sub_operation=None, raw_answers=True, record_type_classname=None):
        """
        Metodo para leer una lista de registros de un base de datos.

        Para efectuar las limitaciones de esta busqueda se usaran los constraints.

        Parameters
        ----------
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para obtener los registros.
        sub_operation: str, opcional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        raw_answers: bool
            Si se desea que la respuesta sea exactamente la devuelta por el driver y no una lista
            de modelos.
            Importante: En este caso el registro 0 contendra la descripcion de los campos para un posible
            uso postproceso.
        record_type_classname: type Model , optional
            El type de la clase del modelo a usar si se requiere que se retorna una lista de modelos
            como respuesta.
            Si raw_answers es False este parametro es obligatorio.

        Returns
        -------
        list[tuple[any]] or list[tuple[Model]]
            la lista de resultados si raw_answers es True o una lista de Modelos
            si raw_answers es False
            Si raw_answers es True el primer resultado en la lsita sera la descripcion
            de los campos.

        Raises
        ------
        PersistenceException
            El  motivo de la excepcion se encuentra en e.persistent_error y puede ser cualquiera
            de los siguientes:
                DB_ERR_SERVERNOTFOUND , si no hay posibilidad de conectarse a la persistencia.
                DB_ERR_CANTEXECUTE    , Error ejecutando la accion , el error exacto ver en el log.
                DB_ERR_ALLOK          , Lectura correcta.

        """
        err_value = PersistenceErrors.DB_ERR_ALLOK

        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug(
                "Error starting transaction fetching records , exception message {} ".format(str(ex)))
            err_value = PersistenceErrors.DB_ERR_SERVERNOTFOUND

        answers = None

        try:
            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()

            # Execute query
            self.__db_delegate.execute_fetch(cursor, c_constraints, sub_operation)

            if raw_answers:
                # Hacemos fetchall pero suponemos que ante una gran cantidad de datos
                # se usaran limites en el query , de lo contrario podemos quedarnos sin
                # memoria.
                # En el elemento 0 de las respuestas ira la descripcion de los campos para
                # poder convertir a modelos o postproceso que pueda requerirse.

                # Punto 1
                # Dado que el driver de mysql soportado y al hecho de un query via callproc
                # bajo ese driver reporta las respuestas de manera no standard a traves de
                # stored_results, verificamos si exsten respuestas en dicho lugar , de no
                # encontrar nada procedemos de la manera habitual.
                if hasattr(cursor, 'stored_results'):
                    for result in cursor.stored_results():
                        answers = result.fetchall()
                        answers.insert(0, result.description)

                # Si no hay respuestas encontradas pasamos al metodo normal.
                if answers is None:
                    answers = cursor.fetchall()
                    answers.insert(0, cursor.description)

            else:
                # Para el caso de raw_answers procedemos a leer en bloques de 100 y los pasamos
                # al modelo correspondiente.
                columns = None
                encodetype = self.__trx_mgr.encoding()

                # Al igual que lo apuntado en el punto 1 , primero buscamos en stored_results , de no haber
                # respuestas seguimos el metodo standard.
                if hasattr(cursor, 'stored_results'):
                    for result in cursor.stored_results():
                        if encodetype:
                            columns = [i[0].encode(encodetype).rstrip('\x00') for i in result.description]
                        else:
                            columns = [i[0] for i in result.description]

                        while True:
                            rows = result.fetchmany(100)
                            if not rows: break

                            for row in rows:
                                # Colocamos la respuesta en el modelo, y lo agregamos a las respuestas
                                model = record_type_classname()
                                model.set_values(dict(zip(columns, row)))
                                answers.append(model)

                # No hay respuestas , procedemos por el metodo standard.
                if answers is None and columns is None:
                    if encodetype:
                        columns = [i[0].encode(encodetype).rstrip('\x00') for i in cursor.description]
                    else:
                        columns = [i[0] for i in cursor.description]

                    while True:
                        rows = cursor.fetchmany(100)
                        if not rows: break

                        for row in rows:
                            # Colocamos la respuesta en el modelo, y lo agregamos a las respuestas
                            model = record_type_classname()
                            model.set_values(dict(zip(columns, row)))
                            if answers is None:
                                answers = []
                            answers.append(model)

            return answers

        except Exception as ex:
            sql = self.__db_delegate.get_fetch_records_query(c_constraints, sub_operation)
            logging.debug(
                "Error reading records , exception message {} , sql ='{}'".format(str(ex), sql))

            if isinstance(ex, PersistenceException):
                err_value = ex.persistent_error
            else:
                err_value = PersistenceErrors.DB_ERR_CANTEXECUTE
            raise Exception() from ex
        finally:
            # Si no es un error terminal cerramos normalmente de lo contrario indicamos
            # que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            if err_value != PersistenceErrors.DB_ERR_ALLOK:
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()

    def get_uid(self, cursor):
        """
        Retornar el id unico del registro.

        Dado que cada driver requiere tratamiento especial para esto , se traslada la
        tarea al DatabaseDelegate.

        Parameters
        ----------
        cursor: Cursor
            El cursor sobre el cual se esta ejecutando la poeracion a la persistencia.

        Returns
        -------
        int
            El unique id o None de no existir.

        """
        return self.__db_delegate.get_uid(cursor)

    def is_duplicate_key_error(self, error_msg):
        """
        Debera indicar si el mensaje de error corresponde a un duplicate key.

        Dado que la especificacion de los drivers de bases de datos existentes no tienen una manera
        standard de codigos de error comun para casos como llave duplicada , se espera que a traves
        del mensaje pueda determinarse si ese es el caso.

        Por default esto es derivado al DatabaseDelegate especifico.

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usado para desambiguar si es un error de llave duplicada o no.

        Returns
        -------
        bool
            True si es un error de llave duplicada , False de lo contrario.

        """
        return self.__db_delegate.is_duplicate_key_error(error_msg)

    def is_foreign_key_error(self, error_msg):
        """
        Debera indicar si el error corresponde a foreign key.

        Dado que la especificacion de los drivers de base de datos existentes no tienen una manera
        standard de codigos de error comun para casos como foreign key , se espera que a traves
        del mensaje pueda determinarse si ese es el caso.

        Por default esto es derivado al DatabaseDelegate especifico.

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por el driver a traves de una exception, el cual sera
            usado para desambiguar si es un error de foreign key o no.

        Returns
        -------
        bool
            True si es un error de foreign key , False de lo contrario.

        """
        return self.__db_delegate.is_foreign_key_error(error_msg)

    def is_record_modified_error(self, error_msg):
        """
        Debera indicar si un registro al hacer update o delete ha sido modificado externamente.

        IMPORTANTE: Este error formalmente no existe en bases de datos y sera usado cuando el
        error de registro modificado sea detectado dentro de un Stored Procedure , queda al
        implementador del mismo mrealizarlo y enviar el error en caso suceda y se requiere
        verificar este hecho.
        Actualmente se espera que el mensaje contenga el texto 'record modified'

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usaso para desambiguar si es un error de registro modificado o no.

        Returns
        -------
        bool
            True si es un error de registro modificado , False de lo contrario.

        """
        if error_msg.find("record modified") >= 0:
            return True
        return False
