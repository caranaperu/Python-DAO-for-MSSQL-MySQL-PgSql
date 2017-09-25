# from abc import ABCMeta
import logging
from Model import Model
from PersistenceErrors import PersistenceErrors
from PersistenceOperations import PersistenceOperations
from TransactionManager import TransactionManager
from DatabaseDelegate import DatabaseDelegate


class DatabasePersistence(PersistenceOperations):
    """
    Clase que efectua las operaciones CRUD a la base de datos sobre un determinado modelo y bajo
    una transaccion.

    Se soporta en un delegate para el caso de base de datos (DatabaseDelegate).

    Examples
        # Es pseudo code
        trx = TransactionManager('mssql', {'host': '192.168.0.9', 'port': '1433',
                                   'user': 'sa', 'password': 'melivane', 'database': 'pytest'})
        db_delegate = DatabaseDelegate()
        dao = DatabasePersistence(trx,db_delegate)

        ret = dao.add(someModel_1)

    Parameters
    trx_mgr: TransactionManager
        Para el control de la transaccion , digase el commit o rollback segun sea necesario.
    db_delegate: DatabaseDelegate
        Para soporte de las operaciones CRUD especificas para base de datos.

    Raises
    ValueError
        En el caso que trx_mgr no sea instancia de TransactionManager
        En el caso que db_delegate no sea instancia de DatabaseDelegate

    """

    def __init__(self, trx_mgr, db_delegate):
        """Initialize  variables."""

        PersistenceOperations.__init__(self)

        # Debe estar definido el transaction manager , verificamos que
        # dicho parametro sea de la instancia correcta.
        if isinstance(trx_mgr, TransactionManager):
            self.__trx_mgr = trx_mgr  # type: TransactionManager
        else:
            raise ValueError(
                'trx_mgr parameter need to be an instance of TransactionManager')

        # El dao delegate es opcional , pero de estar definido debe ser del tipo
        # DAODelegate.
        self.__db_delegate = None
        if db_delegate:
            if isinstance(db_delegate, DatabaseDelegate):
                self.__db_delegate = db_delegate
            else:
                raise ValueError(
                    'db_delegate parameter need to be an instance of DatabaseDelegate')

    def read_record(self, key_values, record_model, c_constraints=None, sub_operation=None):
        """
        Metodo para la lectura de un registro en la base de datos.

        Parameters
        key_values: Union[int,tuple of (str)]
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

            # Usamos este metodo en este caso ya que algunos drivers no devuelven el
            # numero de filas afectadas en forma correcta.
            # Hay que aclarar que esperamos un solo registro de respuesta por ende no hay riesgo
            # en usar fetchall y al menos nos garantizara tener el numero correcto de respuestas.
            rows = cursor.fetchall()
            rowcount = -1
            if rows:
                rowcount = len(rows)

            # Dado que este metodo debe leer un solo registro , si el numero de respuestas
            # es 1 hacemos update al modelo con los valores del registro.
            # Si el numero de registros es cero se entiende que no existe.
            # Si el numero de registros es de mas de 1 se entiende que el query es incorrecto
            if rowcount == 1:
                encodetype = self.__trx_mgr.encoding()
                if encodetype:
                    columns = [i[0].encode(encodetype).rstrip('\x00') for i in cursor.description]
                else:
                    columns = [i[0] for i in cursor.description]

                for col in columns:
                    print(col)
                # Colocamos la respuesta en el modelo.
                record = dict(zip(columns, rows[0]))
                record_model.set_values(record)

                ret_value = PersistenceErrors.DB_ERR_ALLOK
            elif rowcount == 0:
                ret_value = PersistenceErrors.DB_ERR_RECORDNOTFOUND
            else:
                sql = self.__db_delegate.get_read_record_query(key_values, c_constraints, sub_operation)
                logging.debug(
                    "Too many records {} results for read a record with query - {}".format(cursor.rowcount, sql))
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
        record_model: Model
            El modelo de datos conteniendo los datos a agregar.
        c_constraints: Constraints , optional
            Los constraints a aplicar al selector (query) a usarse para agregar el registro.
        sub_operation: str , optional
            cualquier string que describa una sub operacion a ejecutar , por ejemplo :
            "forSelectionList","onlyDates", este valor es libre y sera interpretado por las
            implementaciones especficas de este metodo.
        reread_record: bool , default True
            Si es true , se releera el registro luego de agregarse , esto sera necesario si
            existen campos en el registro que se generan en la persistencia y no del lado del
            usuario.

        Returns
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

    def delete_record(self, key_values, record_version_id=None, verified_delete_check=True):
        # type: (Any,int,bool) -> PersistenceErrors
        return PersistenceErrors.DB_ERR_CANTEXECUTE

    def update_record(self, record_model, sub_operation=None):
        # type: (Model,str) -> PersistenceErrors
        return PersistenceErrors.DB_ERR_CANTEXECUTE

    def get_uid(self, cursor):
        """
        Retornar el id unico del registro.

        Dado que cada driver requiere tratamiento especial para esto , se traslada la
        tarea al DatabaseDelegate.

        Parameters
        cursor: Cursor
            El cursor sobre el cual se esta ejecutando la poeracion a la persistencia.

        Returns
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
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usado para desambiguar si es un error de llave duplicada o no.

        Returns
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
        error_msg: str
            Con el mensaje retornado por el driver a traves de una exception, el cual sera
            usado para desambiguar si es un error de foreign key o no.

        Returns
        bool
            True si es un error de foreign key , False de lo contrario.

        """
        return self.__db_delegate.is_foreign_key_error(error_msg)
