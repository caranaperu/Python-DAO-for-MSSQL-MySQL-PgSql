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

test = 'without_uid'
test = 'del_fk'

class PgSQLDAODelegate(DatabaseDelegate):
    __metaclass__ = ABCMeta

    def __init__(self):
        DatabaseDelegate.__init__(self)

    def is_duplicate_key_error(self, error_msg):
        if error_msg.find("duplicate key value violates unique constraint") >= 0:
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # El primer chequeo es para odbc drivers , el otro es para pymssql
        if error_msg.find("violates foreign key constraint") >= 0:
            return True
        return False

    def get_uid(self, handler):
        if hasattr(handler, 'lastrowid'):
            return handler.lastrowid
        return None


driver = 'pgsql'
trx = TransactionManager(driver, {'host': '192.168.0.5','port':'5432', 'user': 'postgres', 'password': 'melivane',
                                  'database': 'db_pytest'})


class DAODelegateTest(PgSQLDAODelegate):
    def __init__(self):
        PgSQLDAODelegate.__init__(self)

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
            return "select * from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(key_values[0],key_values[1])

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        return "insert into tb_maintable(id_key,anytext) values (DEFAULT,'{}') returning id_key".format(record_model.anytext)

    def get_update_record_query(self, record_model, sub_operation=None):
        return "update tb_maintable set anytext = '{}' where id_key = {}".format(record_model.anytext,record_model.id_key)

    def get_delete_record_query(self, key_values):
        if test == 'normal':
            return "delete from tb_maintable where id_key = {}".format(key_values)
        elif test == 'del_fk':
            return "delete from tb_testfk where fktest = {}".format(key_values)
        else:
            return "delete from tb_maintable_ckeys where main_code = '{}' and main_number = {}".format(key_values[0],key_values[1])


daoDelegate = DAODelegateTest()

# daoDelegate.set_add_definition()
# daoDelegate.set_read_definition()

dao = DatabasePersistence(trx, daoDelegate)

# usamos la transacion para informar que el control es extrerno.
if test == 'normal':
    ret = dao.delete_record(1)
elif test == 'del_fk':
    ret = dao.delete_record(1)
else:
    ret = dao.delete_record(('008',8))
print(ret)



