from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import MsSQLBaseDelegate
import logging

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# test = 'without_uid'
test = 'del_fk'
# test = 'normal'


driver = 'mssql'
trx = TransactionManager(driver, {'dsn': 'MSSQLServer', 'host': '192.168.0.2', 'port': '1433',
                                  'user': 'sa', 'password': 'Melivane100', 'database': 'db_pytest'})


class DAODelegateTest(MsSQLBaseDelegate):
    def __init__(self):
        MsSQLBaseDelegate.__init__(self)

    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        if test == 'normal':
            return "select * from tb_maintable where pk_id={}".format(key_values)
        elif test == 'del_fk':
            return "select * from tb_testfk where fktest={}".format(key_values)
        else:
            return "select * from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(key_values[0],
                                                                                                         key_values[1])

    def get_delete_record_query(self, key_values, c_constraints=None, sub_operation=None):
        if test == 'normal':
            return "delete from tb_maintable where pk_id = {}".format(key_values)
        elif test == 'del_fk':
            return "delete from tb_testfk where fktest = {}".format(key_values)
        else:
            return "delete from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(key_values[0],
                                                                                                       key_values[1])


daoDelegate = DAODelegateTest()
dao = DatabasePersistence(trx, daoDelegate)

# usamos la transacion para informar que el control es extrerno.
if test == 'normal':
    ret = dao.delete_record(4)
elif test == 'del_fk':
    ret = dao.delete_record(1)
else:
    ret = dao.delete_record(('008', 7))
print(ret)
