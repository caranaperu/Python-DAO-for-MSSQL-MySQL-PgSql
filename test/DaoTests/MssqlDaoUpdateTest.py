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
        self.pk_id = None
        self.anytext = None
        self.version_row= None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('pk_id',)

    # retornar None si no se desea chequeo de version
    def get_record_version_field(self):
        return 'version_row'


class MSDAODelegate(DatabaseDelegate):
    __metaclass__ = ABCMeta

    def __init__(self):
        DatabaseDelegate.__init__(self)

    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        if (error_msg.find("DB-Lib error message 2627, severity 14") >= 0 or error_msg.find(
                "DB-Lib error message 2601, severity 14") >= 0
            or error_msg.find('Violation of UNIQUE KEY constraint') >= 0 or error_msg.find(
            'Cannot insert duplicate key row')) >= 0:
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool

        # El primer chequeo es para odbc drivers , el otro es para pymssql
        if ((error_msg.find("DB-Lib error message 547, severity 16") >= 0 and error_msg.find(
                "FOREIGN KEY constraint") >= 0)
            or error_msg.find("conflicted with the FOREIGN KEY constraint") >= 0):
            return True
        return False

    def get_uid(self, handler):
        if hasattr(handler, 'lastrowid'):
            return handler.lastrowid
        return None



driver = 'mssql'
trx = TransactionManager(driver, {'dsn': 'MSSQLServer', 'host': '192.168.0.9', 'port': '1433',
                                  'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})

class DAODelegateTest(MSDAODelegate):
    def __init__(self):
        MSDAODelegate.__init__(self)

    def get_uid(self, cursor):
        # Es irrelevante si un trigger inserta a la misma tabla.
        cursor.execute("select SCOPE_IDENTITY();")
        lastrowid = cursor.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
        return lastrowid

    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        return "select * from tb_maintable where pk_id={}".format(key_values)

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        return "insert into tb_maintable(anytext) values ('{}')".format(record_model.anytext)

    def get_update_record_query(self, record_model, sub_operation=None):
        return "update tb_maintable set anytext = '{}' where pk_id = {}".format(record_model.anytext,record_model.pk_id)


model = MainTableModel()

daoDelegate = DAODelegateTest()

# daoDelegate.set_add_definition()
# daoDelegate.set_read_definition()

dao = DatabasePersistence(trx, daoDelegate)

ret = dao.read_record(1,model)
model.anytext = 'testchang9'
print(model.__dict__)

#model.version_row = '0x10'

# usamos la transacion para informar que el control es extrerno.
ret = dao.update_record(model)
print(ret)
print(model.__dict__)



