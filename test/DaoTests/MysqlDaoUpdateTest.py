import sys

sys.path.insert(0, '/home/carana/PycharmProjects/test')

from TransactionManager import TransactionManager
from DatabasePersistence import DatabasePersistence
from DatabaseDelegate import DatabaseDelegate
from Model import Model
import logging

from abc import ABCMeta

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)



class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.id_key = None
        self.anytext = None
        self.updated_when= None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('id_key',)

    # retornar None si no se desea chequeo de version
    def get_record_version_field(self):
        return 'updated_when'


class MySQLDAODelegate(DatabaseDelegate):
    __metaclass__ = ABCMeta

    def __init__(self):
        DatabaseDelegate.__init__(self)

    def is_duplicate_key_error(self, error_msg):
        if error_msg.find("(23000): Duplicate entry") >= 0:
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # El primer chequeo es para odbc drivers , el otro es para pymssql
        if (error_msg.find("conflicted with the FOREIGN KEY constraint") >= 0
                or error_msg.find("a foreign key constraint fails") >= 0):
            return True
        return False

    def get_uid(self, handler):
        if hasattr(handler, 'lastrowid'):
            return handler.lastrowid
        return None



driver = 'mysql'
trx = TransactionManager(driver, {'host': 'localhost', 'port': '3306',
                                  'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})

class DAODelegateTest(MySQLDAODelegate):
    def __init__(self):
        MySQLDAODelegate.__init__(self)

    def get_uid(self, cursor):
        # El stored procedure debe hacer solo insert a la tabla que se requeire el id o el insert debe ser
        # el ultimo dentro del sp, es irrelevante si tiene selects o no ya que seran ignorados.
        # IMPORTANTE : Si se hace mas de un insert en la misma tabla el id sera del ultimo insert
        #   esto es absolutamente raro en produccion , pero valga la advertencia.
        # En el caso se agrege a otras tablas debera usarse otro type mas adecuado, la idea aqui es que solo se agregue
        # a la tabla de interes en el sp.
        #
        # El last insert id no toma en cuenta lo que suceda dentro de un trigger.
        #
        # En este caso lastrowid del cursor no retorna un valor valido.
        cursor.execute("SELECT last_insert_id();")
        lastrowid = cursor.fetchone()[0]
        print(lastrowid)
        return lastrowid

    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        return "select * from tb_maintable where id_key={}".format(key_values)

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        return "insert into tb_maintable(anytext) values ('{}') returning id_key".format(record_model.anytext)

    def get_update_record_query(self, record_model, sub_operation=None):
        return "update tb_maintable set anytext = '{}' where id_key = {}".format(record_model.anytext,record_model.id_key)
        #return "select dpupdatetest({},'{}');".format(record_model.id_key,record_model.anytext)

model = MainTableModel()
model.anytext = 'testchang7'
model.id_key = 74
model.updated_when = '2017-10-02 05:20:36'


daoDelegate = DAODelegateTest()

# daoDelegate.set_add_definition()
# daoDelegate.set_read_definition()

dao = DatabasePersistence(trx, daoDelegate)

# usamos la transacion para informar que el control es extrerno.
ret = dao.update_record(model)
print(ret)
print(model.__dict__)



