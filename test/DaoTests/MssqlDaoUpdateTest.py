from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.persistence.PersistenceErrors import PersistenceErrors
from carlib.database.impl import MsSQLBaseDelegate
from carlib.persistence.Model import Model
import logging

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
        self.version_row = None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('pk_id',)

    # retornar None si no se desea chequeo de version
    def get_version_field(self):
        return 'version_row'


driver = 'mssql'
trx = TransactionManager(driver, {'dsn': 'MSSQLServer', 'host': '192.168.0.2', 'port': '1433',
                                  'user': 'sa', 'password': 'Melivane100', 'database': 'db_pytest'})


class DAODelegateTest(MsSQLBaseDelegate):
    def __init__(self):
        MsSQLBaseDelegate.__init__(self)

    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        return "select * from tb_maintable where pk_id={}".format(key_values)

    def get_update_record_query(self, record_model, c_constraints=None, sub_operation=None):
        return "update tb_maintable set anytext = '{}' where pk_id = {}".format(record_model.anytext,
                                                                                record_model.pk_id)


model = MainTableModel()

daoDelegate = DAODelegateTest()

dao = DatabasePersistence(trx, daoDelegate)

ret = dao.read_record(1, model)
print(ret)
if ret == PersistenceErrors.DB_ERR_ALLOK:
    print(model.__dict__)
    model.anytext = 'testchang6'

    # usamos la transacion para informar que el control es extrerno.
    ret = dao.update_record(model)
    print(ret)
    print(model.__dict__)
