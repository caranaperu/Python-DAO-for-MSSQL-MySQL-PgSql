from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import PgSQLBaseDelegate
import logging

from carlib.persistence.Constraints import Constraints

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# test = 'without_uid'
# test = 'del_fk'
test = 'normal'

calltest = True

driver = 'pgsql'
trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '5432', 'user': 'postgres', 'password': 'melivane',
                                  'database': 'db_pytest'})


class DAODelegateTest(PgSQLBaseDelegate):
    def __init__(self):
        PgSQLBaseDelegate.__init__(self)
        if calltest:
            self.delete_definition={'is_call': True}

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
        if test == 'normal':
            return "select *,xmin from tb_maintable where id_key={}".format(key_values)
        elif test == 'del_fk':
            return "select * from tb_testfk where fktest={}".format(key_values)
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
                return "delete from tb_testfk where fktest = {}".format(key_values)
        else:
            if calltest:
                return 'dpdeletetest_ckeys'
            else:
                return "delete from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(key_values[0],
                                                                                                       key_values[1])


daoDelegate = DAODelegateTest()

dao = DatabasePersistence(trx, daoDelegate)

constraints = None
if calltest:
    constraints = Constraints()

# usamos la transacion para informar que el control es extrerno.
# IMPORTANTE:
# Si usa sp para eliminar y verified_delete_check es true el parametro
# key_values deben ser iguales a lo de los caller params en los constraints.

if test == 'normal':
    key = 15
    if calltest:
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL,key,0)
    ret = dao.delete_record(key,c_constraints=constraints)
elif test == 'del_fk':
    key = 1
    if calltest:
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL,key,0)
    ret = dao.delete_record(key,c_constraints=constraints)
else:
    key=('010', 11)
    if calltest:
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL,key[0],0)
        constraints.add_caller_parameter(Constraints.CallerOperation.DEL, key[1], 0)
    ret = dao.delete_record(key,c_constraints=constraints)
print(ret)
