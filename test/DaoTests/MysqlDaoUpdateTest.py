from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import MySQLBaseDelegate
from carlib.persistence.Model import Model
from carlib.persistence.Constraints import Constraints

import logging

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
        self.updated_when = None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('id_key',)

    # retornar None si no se desea chequeo de version
    def get_version_field(self):
        return 'updated_when'


driver = 'mysql'
calltest = False
read_calltest = False

trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '3306',
                                  'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})


class DAODelegateTest(MySQLBaseDelegate):
    def __init__(self):
        MySQLBaseDelegate.__init__(self)
        if calltest:
            self.update_definition = {'is_call': True}
        if read_calltest:
            self.read_definition = {'is_call': True}

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
        if read_calltest:
            return 'dpreadtest'
        else:
            return "select * from tb_maintable where id_key={}".format(key_values)

    def get_update_record_query(self, record_model, c_constraints=None, sub_operation=None):
        if calltest:
            return "dpupdatetest"
        else:
            return "update tb_maintable set anytext = '{}' where id_key = {}".format(record_model.anytext,
                                                                                     record_model.id_key)


model = MainTableModel()
model.anytext = 'testchang6'
model.id_key = 78
model.updated_when = '2017-10-29 23:19:09'

constraints = None

if calltest:
    constraints = Constraints()
    constraints.add_caller_parameter(Constraints.CallerOperation.UPD, 'id_key', 0)
    constraints.add_caller_parameter(Constraints.CallerOperation.UPD, 'anytext', 1)

if read_calltest:
    if constraints is None:
        constraints = Constraints()
    constraints.add_caller_parameter(Constraints.CallerOperation.READ, model.id_key, 0)

daoDelegate = DAODelegateTest()

dao = DatabasePersistence(trx, daoDelegate)

# usamos la transacion para informar que el control es extrerno.
ret = dao.update_record(model, c_constraints=constraints)
print(ret)
print(model.__dict__)
