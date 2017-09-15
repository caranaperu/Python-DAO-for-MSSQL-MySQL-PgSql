from abc import ABCMeta
import logging
from typing import Any
from BaseModel import BaseModel
from DAOConstraints import DAOConstraints
from DAOErrorConstants import DAOErrorConstants
from DAOOperations import DAOOperations
from TransactionManager import TransactionManager

class DAOBase(DAOOperations):
    """Clase abstracta que define la implementacion base de las operaciones del DAO."""
    __metaclass__ = ABCMeta

    def __init__(self, trx_mgr):
        # type: (TransactionManager) -> None
        """Initialize  variables."""

        DAOOperations.__init__(self)

        if (isinstance(trx_mgr, TransactionManager)):
            self.__trx_mgr = trx_mgr  # type: TransactionManager
        else:
            raise ValueError(
                'trx_mgr parameter need to be an instance of TransactionManager')

    def get_column_names(self,cursor, table_name):
        with cursor:
            cursor.execute("SELECT * FROM " + table_name)
            column_names = [desc[0] for desc in cursor.description]
            cursor.fetchall()
        return column_names

    def read_record(self, key_value, record_model, c_constraints=None, sub_operation=None):
        # type: (Any,BaseModel,DAOConstraints,str) -> DAOErrorConstants
        """
        Metodo para la lectura especifica de un solo record basado en el key_value.

        El armado del query es derivado al metodo get_record_query el cual debe ser
        implementado por las clases especificas derivadas de esta.
        """
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug("Error starting transaction reading record with key {} , exception message {} ".format(
                key_value, str(ex)))
            return DAOErrorConstants.DB_ERR_SERVERNOTFOUND

        ret_value = None
        sql = None

        try:

            sql = self.get_read_record_query(
                key_value, c_constraints, sub_operation)

            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()
            #columns = self.get_column_names(cursor,'tb_maintable');
            #for col in columns:
            #    print(type(col))
            #    #print(col)
            #    print(col.encode('utf-16le'))
            # read record
            cursor.execute(sql)
            rows = cursor.fetchall()

            """  Usamos este metodo en este caso ya que algunos drivers no devuelven el
                 numero de filas afectadas en forma correcta.
            """
            rowcount = -1
            if rows:
                rowcount = len(rows)

            """
            Dado que este metodo debe leer un solo registro , si el numero de respuestas
            es 1 hacemos update al modelo con los valores del registro.
            Si el numero de registros es cero se entiende que no existe.
            Si el numero de registros es de mas de 1 se entiende que el query es incorrecto
            """
            if (rowcount == 1):
                columns = [i[0] for i in cursor.description]
                for col in columns:
                    print(col)

                encodetype = self.__trx_mgr.encoding()
                if encodetype:
                    columns = [i[0].encode('utf-16le').rstrip('\x00') for i in cursor.description]
                else:
                    columns = [i[0] for i in cursor.description]

                for col in columns:
                    print(col)
                #for col in columns:
                #    print (format(col))
                record = dict(zip(columns, rows[0]))
                record_model.set_values(record)

                ret_value = DAOErrorConstants.DB_ERR_ALLOK
            elif (rowcount == 0):
                ret_value = DAOErrorConstants.DB_ERR_RECORDNOTFOUND
            else:
                logging.debug(
                    "Too many records {} results for read a record with query - {}".format(cursor.rowcount, sql))
                ret_value = DAOErrorConstants.DB_ERR_TOOMANYRESULTS
        except Exception as ex:
            logging.debug("Error reading record with key {} , exception message {}, sql = '{}'".format(
                key_value, str(ex), sql))
            ret_value = DAOErrorConstants.DB_ERR_CANTEXECUTE
        finally:
            """
             Si no es un error terminal cerramos normalmente de lo contrario indicamos
             que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            """
            if (ret_value != DAOErrorConstants.DB_ERR_ALLOK and
                    ret_value != DAOErrorConstants.DB_ERR_RECORDNOTFOUND):
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()
        return ret_value

    def delete_record(self, record_id, record_version_id, verified_delete_check=True):
        # type: (Any,int,bool) -> DAOErrorConstants
        return DAOErrorConstants.DB_ERR_CANTEXECUTE

    def add_record(self, record_model, query_type=DAOOperations.QueryType.DIRECT_CALL, c_constraints=None, sub_operation=None, rereadRecord=True):
        # type: (BaseModel,QueryType,DAOConstraints,str, bool) -> DAOErrorConstants
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug(
                "Error starting transaction adding a record , exception message {} ".format(str(ex)))
            return DAOErrorConstants.DB_ERR_SERVERNOTFOUND

        ret_value = None
        sql = None
        try:
            sql = self.get_add_record_query(
                record_model, c_constraints, sub_operation)

            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()
            # add record
            cursor.execute(sql)
            print("Row Count = {}".format(cursor.rowcount))

            # No funciona com pymssal ya que parece alterar la posicion del cursor.
            #if hasattr(cursor,'lastrowid'):
            #    print("Last Row Id = {}".format(cursor.lastrowid))

            if rereadRecord:
                if not record_model.is_UID_pk():
                    pk_keys = record_model.get_pk_fields()
                else:
                    #lastrowid = cursor.fetchone()[0]
                    #print("lastrowid = {}".format(lastrowid))
                    pk_keys = self.get_UID(cursor, query_type)

                ret_value = self.read_record(
                    pk_keys, record_model, c_constraints, sub_operation)
            else:
                ret_value = DAOErrorConstants.DB_ERR_ALLOK
        except Exception as ex:
            if self.is_duplicate_key_error(str(ex)):
                logging.debug(
                    "Error adding record , ya existe un registro con la misma llave,sql = '{}'".format(sql))
                ret_value = DAOErrorConstants.DB_ERR_RECORDEXIST
            elif self.is_foreign_key_error(str(ex)):
                logging.debug(
                    "Error adding record , foreign key error,sql = '{}'".format(sql))
                ret_value = DAOErrorConstants.DB_ERR_FOREIGNKEY
            else:
                logging.debug(
                    "Error adding record , exception message {} , sql ='{}'".format(str(ex), sql))
                ret_value = DAOErrorConstants.DB_ERR_CANTEXECUTE
        finally:
            """
             Si no es un error terminal cerramos normalmente de lo contrario indicamos
             que existe un error lo cual causara que se cierre la transaccion y se hara un rollback
            """
            if (ret_value != DAOErrorConstants.DB_ERR_ALLOK):
                self.__trx_mgr.end_transaction(True)
            else:
                self.__trx_mgr.end_transaction()
        return ret_value

    def update_record(self, record_model, sub_operation=None):
        # type: (BaseModel,str) -> DAOErrorConstants
        return DAOErrorConstants.DB_ERR_CANTEXECUTE
