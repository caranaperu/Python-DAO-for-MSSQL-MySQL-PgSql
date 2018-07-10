from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import PgSQLBaseDelegate
from carlib.persistence.Constraints import Constraints
from carlib.persistence.Model import Model
import logging

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

calltest = True
calltest_execute = True


class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.id_key = None
        self.anytext = None
        self.xmin = None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('id_key',)

    # retornar None si no se desea chequeo de version
    def get_version_field(self):
        return 'xmin'


driver = 'pgsql'
trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '5432', 'user': 'postgres', 'password': 'melivane',
                                  'database': 'db_pytest'})


class DAODelegateTest(PgSQLBaseDelegate):
    def __init__(self):
        PgSQLBaseDelegate.__init__(self)
        if calltest_execute:
            self.update_definition = {'is_call': True}

    def get_uid(self, cursor):
        # La mejor manera que existe en postgres es usar la clausula returning con el id
        # es infailble bajo cualquier situacion y mas confiable en multiuser.
        # Importante si se desea usar POSTGRES-XC es necesario usar currval.
        #           Asi mismo para postgres < 8.2 esa seria la solucion ya que no existe el returning.
        # hay que agregar que lastrowid del cursor no retorna un valor correcto los autores de psycopg2
        # no lo recomiendan.
        # El metodo returning es infalibe en el extrano caso que un trigger insertara otro registro
        # a la misma tabla (caso muy remoto).
        lastrowid = cursor.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
        return lastrowid

    def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
        return "select *,xmin from tb_maintable where id_key={}".format(key_values)

    def get_update_record_query(self, record_model, c_constraints=None, sub_operation=None):
        if calltest_execute:
            return "dpupdatetest"
        elif calltest:
            return "select dpupdatetest({},'{}');".format(record_model.id_key, record_model.anytext)
        else:
            return "update tb_maintable set anytext = '{}' where id_key = {}".format(record_model.anytext,
                                                                                     record_model.id_key)


model = MainTableModel()
model.anytext = 'testchang4'
model.id_key = 5
model.xmin = 128951

constraints = None
if calltest_execute:
    constraints = Constraints()
    constraints.add_caller_parameter(Constraints.CallerOperation.UPD, 'id_key', 0)
    constraints.add_caller_parameter(Constraints.CallerOperation.UPD, 'anytext', 0)

daoDelegate = DAODelegateTest()
dao = DatabasePersistence(trx, daoDelegate)

# usamos la transacion para informar que el control es extrerno.
ret = dao.update_record(model, c_constraints=constraints)
print(ret)
print(model.__dict__)
