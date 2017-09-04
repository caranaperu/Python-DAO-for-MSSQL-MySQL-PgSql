
from abc import ABCMeta, abstractmethod
from enum import Enum
from BaseModel import BaseModel
from DAOErrorConstants import DAOErrorConstants
from DAOConstraints import DAOConstraints


class DAOOperations(object):

    """Clase abstracta que define las operaciones validas que implementara un DAO."""

    __metaclass__ = ABCMeta

    class QueryType(Enum):
        """Enumeracion que contiene los tipos de query soportados.

        CASO MSSQL:
        - DIRECT_CALL cuando se imputa en el execute el query directo , no sp
            En este caso aunque haya triggers la DB retornara el lastrowid en forma
            correcta exista triggers o no.
            Este caso se refiere a:
                INSERT INTO table(f1,f2,...) values(v1,v2,....)
        """
        DIRECT_CALL = 0
        SP_CALL = 1
        DIRECT_WITH_RETURNING = 2

    @abstractmethod
    def read_record(self, key_value, record_model, c_constraints=None, sub_operation=None):
        # type: (Any,BaseModel,DAOConstraints,str) -> DAOErrorConstants
        pass

    @abstractmethod
    def delete_record(self, record_id, record_version_id, verified_delete_check=True):
        # type: (Any,int,bool) -> DAOErrorConstants
        pass

    @abstractmethod
    def add_record(self, record_model, query_type=QueryType.DIRECT_CALL, c_constraints=None, sub_operation=None):
        # type: (BaseModel,QueryType,DAOConstraints,str) -> DAOErrorConstants
        pass

    @abstractmethod
    def update_record(self, record_model, sub_operation=None):
        # type: (BaseModel,str) -> DAOErrorConstants
        pass

    """
    Helpers para que cada DAO en forma especifica retorne el SQL query para cada
    operacion.
    """
    @abstractmethod
    def get_read_record_query(self, key_value, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) -> str
        pass

    @abstractmethod
    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (BaseModel,DAOConstraints,str) -> str
        pass

    """
    Helpers para que cada DAO en forma especifica indique si el error en una determianda
    base de datos o persistencia corresponde a ciertos casos excepcionales , como llave
    duplicada o foreign key error u otros.
    Dado que el dbapi 2.0 no indica con claridad que contiene una excepcion , digase el
    codigo de error , pero si se garantiza por parte de las persistencias que el mensaje
    de error es unico en vada uno de los casos , enviamos el mensaje de la excepcion para
    se parsee y se determine si existe el error.
    """
    @abstractmethod
    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        pass

    @abstractmethod
    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool
        pass

    def get_last_rowid(self):
        return None


if __name__ == "__main__":
    class DAOOperations2(DAOOperations):

        def read_record(self, key_value, record_model, c_constraints=None, sub_operation=None):
            # type: (BaseModel,str) -> DAOErrorConstants
            return DAOErrorConstants.DB_ERR_ALLOK

    # Esto enviara un error ya que no puede instanciarse una clase que es
    # abstracta. Tambiewn indicara que el primer parametro a read record es invalido
    bmodel = BaseModel()
    do_oper = DAOOperations()
    answer = do_oper.read_record(bmodel, "rrr", None)

    answer = do_oper.read_record("bmodel", "rrr", None)
