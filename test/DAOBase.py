from abc import ABCMeta
import logging
from typing import Any
from BaseModel import BaseModel
from DAOConstraints import DAOConstraints
from DAOErrorConstants import DAOErrorConstants
from DAOOperations import DAOOperations
from TransactionManager import TransactionManager

from datetime import date

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

        try:
            sql = self.get_read_record_query(
                key_value, c_constraints, sub_operation)

            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()
            # read record
            cursor.execute(sql)
            rows = cursor.fetchall()

            """
            Dado que este metodo debe leer un solo registro , si el numero de respuestas
            es 1 hacemos update al modelo con los valores del registro.
            Si el numero de registros es cero se entiende que no existe.
            Si el numero de registros es de mas de 1 se entiende que el query es incorrecto
            """
            if (cursor.rowcount == 1):
                columns = [i[0] for i in cursor.description]
                record = dict(zip(columns, rows[0]))
                record_model.set_values(record)

                ret_value = DAOErrorConstants.DB_ERR_ALLOK
            elif (cursor.rowcount == 0):
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

    def add_record(self, record_model, query_type=DAOOperations.QueryType.DIRECT_CALL, c_constraints=None, sub_operation=None):
        # type: (BaseModel,QueryType,DAOConstraints,str) -> DAOErrorConstants
        try:
            self.__trx_mgr.start_transaction()
        except Exception as ex:
            logging.debug(
                "Error starting transaction adding a record , exception message {} ".format(str(ex)))
            return DAOErrorConstants.DB_ERR_SERVERNOTFOUND

        ret_value = None
        try:
            sql = self.get_add_record_query(
                record_model, c_constraints, sub_operation)

            # Open the transaction
            cursor = self.__trx_mgr.get_transaction_cursor()
            # add record
            cursor.execute(sql)
          #  out = cursor.callproc("uspaddFactura4",(record_model.factura_id,record_model.name));
          #  print(out)

            print(cursor.rowcount)
            print(cursor.lastrowid)


            unique_id = None
            if query_type == DAOOperations.QueryType.DIRECT_CALL:
                if cursor.rowcount <= 0:
                    ret_value = DAOErrorConstants.DB_ERR_CANTEXECUTE
                else:
                    unique_id = record_model.get_unique_id()
                    print("El unique id es = {}".format(unique_id))
                    if not unique_id:
                        if record_model.is_pk_identity():
                            print("Es PK")
                            """
                            IMPORTANTE:
                                - Para mysql LAST_INSERT_ID garantiza que sera del primer insert en la transaccion
                                    independiente del numero de inserts que se hagan en la misma transaccion.
                            """
                            unique_id = cursor.lastrowid
                            print("PK id  es = {}".format(unique_id))
            elif query_type == DAOOperations.QueryType.SP_CALL:
                unique_id = record_model.get_unique_id()
                print("El unique id en sp_call es = {}".format(unique_id))
                if not unique_id:
                    print("Verificando rows")
                    rows = cursor.fetchone()
                    if rows:
                        unique_id = rows[0]
                        print(rows[0])

            if unique_id:
                ret_value = self.read_record(
                    unique_id, record_model, c_constraints, sub_operation)
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
