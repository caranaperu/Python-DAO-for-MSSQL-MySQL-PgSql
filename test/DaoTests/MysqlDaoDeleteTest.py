from carlib.persistence.Constraints import Constraints
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import MySQLBaseDelegate
import logging

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

test = 'without_uid'
# test = 'del_fk'
# test = 'normal'

calltest = True

driver = 'mysql'
trx = TransactionManager(driver, {'host': 'localhost', 'port': '3306',
                                  'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})


class DAODelegateTest(MySQLBaseDelegate):
    def __init__(self):
        MySQLBaseDelegate.__init__(self)
        if calltest:
            self.delete_definition = {'is_call': True}

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
        if test == 'normal':
            return "select * from tb_maintable where id_key={}".format(key_values)
        elif test == 'del_fk':
            return "select * from tb_testfk where fk_test={}".format(key_values)
        else:
            return "select * from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(key_values[0],
                                                                                                         key_values[1])

    def get_delete_record_query(self, key_values, c_constraints=None, sub_operation=None):
        if test == 'normal':
            if calltest:
                return 'dpdeletetest'
            else:
                return "delete from tb_maintable where id_key = {}".format(key_values)
        elif test == 'del_fk':
            if calltest:
                return 'dpdeletetest_fk'
            else:
                return "delete from tb_testfk where fk_test = {}".format(key_values)
        else:
            if calltest:
                return 'dpdeletetest_ckeys'
            else:
                return "delete from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(
                    key_values[0], key_values[1])


daoDelegate = DAODelegateTest()

dao = DatabasePersistence(trx, daoDelegate)

constraints = None

# usamos la transacion para informar que el control es extrerno.
if test == 'normal':
    key = 101
    if calltest:
        constraints = Constraints()
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL, key, 0)

    ret = dao.delete_record(key, c_constraints=constraints)
elif test == 'del_fk':
    key = 1
    if calltest:
        constraints = Constraints()
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL, key, 0)
    ret = dao.delete_record(key, c_constraints=constraints)
else:
    keys = ('008', 8)
    if calltest:
        constraints = Constraints()
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL, keys[0], 0)
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL, keys[1], 1)
    ret = dao.delete_record(keys, c_constraints=constraints)
    # ret = dao.delete_record(None, c_constraints=constraints, verified_delete_check=False)
print(ret)
