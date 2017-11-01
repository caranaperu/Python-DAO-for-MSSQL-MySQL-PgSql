from carlib.utils import cls_locked_attrs

@cls_locked_attrs
class A:
    def __init__(self):
        self._a = 0

a = A()
a._a = 1
#a.b = 2

class B(A):
    def __init__(self):
        A.__init__(self)
        self._c = 0
        self._d = 0

b = B()
b._c = 1
b._d = 2
#b.test = 3
print(b._c)

import sys

sys.path.insert(0, '/home/carana/PycharmProjects/test')

from carlib.persistence.Model import Model


def func1(classType):
    c = classType()
    c.id_key = 100
    print(c.__dict__)



from carlib.database.DatabaseDelegate import DatabaseDelegate
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
import logging
import mem_profile
import time
from carlib.persistence.Constraints import Constraints
from carlib.utils import dbutils

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

from abc import ABCMeta

driver = 'pgsql'
calltest = False

if driver != 'mssql':
    class MainTableModel(Model):
        def __init__(self):
            Model.__init__(self)
            self.id_key = None
            self.anytext = None

        def is_pk_uid(self):
            return True

        def get_pk_fields(self):
            return ('id_key',)

        # retornar None si no se desea chequeo de version
        def get_version_field(self):
            return 'updated_when'
else:
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

class DAODelegateTest(PgSQLDAODelegate):
    def __init__(self):
        PgSQLDAODelegate.__init__(self)
        if calltest == True:
            self.fetch_definition = {'is_call': True, 'call_parameters':None}

    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):

        if driver == 'pgsql':
            if calltest == False:
                sql = "select * from c_invoice"
                if c_constraints:
                    sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)

                    if c_constraints.offset:
                        sql = sql + " OFFSET " + str(c_constraints.offset)
                    if c_constraints.limit:
                        sql = sql + " LIMIT " + str(c_constraints.limit - c_constraints.offset)
            else:
                self.fetch_definition['call_parameters']=['1009790']
                sql = "fetch_results"

        elif driver == 'mssql':
            ## pyodbc y familia NO SOPRTAN CALL PROC
            if calltest == True:
                self.fetch_definition['is_call'] = False
                sql = "EXEC fetch_results ;"
            else:
                if c_constraints:
                    sql = "select"
                    if c_constraints.limit and c_constraints.offset == 0:
                        sql= sql+" top "+str(c_constraints.limit) + " * from veritrade"
                    elif c_constraints.limit-c_constraints.offset > 0:
                        sql= sql+" * from(select *,row_number() over(order by (select null)) as row from veritrade)m "
                        sql= sql+" where row between "+str(c_constraints.offset) + " and " + str(c_constraints.limit)
                        sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)
                    else:
                        sql = " * from veritrade"
                else:
                    sql = "select  * from veritrade"

        else:
            if calltest == False:
                sql = "select * from tb_maintable"

                if c_constraints:
                    sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)

                    if c_constraints.limit:
                        sql = sql + " LIMIT " + str(c_constraints.limit - c_constraints.offset)
                    if c_constraints.offset:
                        sql = sql + " OFFSET " + str(c_constraints.offset)
            else:
                self.fetch_definition['call_parameters']=['2294']
                sql = "fetch_results"

        print (sql)
        return sql




if driver == 'pgsql':
    trx = TransactionManager(driver, {'host': '192.168.0.5','port':'5432', 'user': 'postgres', 'password': 'melivane',
                                      'database': 'xendra'})
elif driver == 'mysql':
    trx = TransactionManager(driver, {'host': 'localhost', 'port': '3306',
                                      'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})
else:
    trx = TransactionManager(driver, {'dsn': 'MSSQLServer', 'host': '192.168.0.9', 'port': '1433',
                                      'user': 'sa', 'password': 'melivane', 'database': 'veritrade'})
daoDelegate = DAODelegateTest()
dao = DatabasePersistence(trx, daoDelegate)

memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

constraint = Constraints()
constraint.offset = 0
constraint.limit = 50

if driver == 'pgsql':
    constraint.add_filter_field('issotrx',True,Constraints.FilterType.EQUAL)
    constraint.add_filter_field('c_bpartner_id',1009790,Constraints.FilterType.NO_EQUAL)
    constraint.add_filter_field('c_groupdoc_id',None,Constraints.FilterType.NO_EQUAL)
    constraint.add_filter_field('docaction','cl',Constraints.FilterType.IPARTIAL)

    constraint.add_sort_field('c_groupdoc_id',Constraints.SortType.ASC)
    constraint.add_sort_field('c_bpartner_id',Constraints.SortType.DESC)
elif driver == 'mssql':
    constraint.add_filter_field('importador', 'NISSAN', Constraints.FilterType.IPARTIAL)
    # Sort
    constraint.add_sort_field('pais_embarque', Constraints.SortType.ASC)
elif driver == 'mysql':
    constraint.add_filter_field('anytext','Test23',Constraints.FilterType.EQUAL)
    constraint.add_filter_field('id_key',40,Constraints.FilterType.GREAT_THAN_EQ)
    # Sort
    constraint.add_sort_field('id_key',Constraints.SortType.ASC)

rows = dao.fetch_records(constraint, raw_answers= False, record_type_classname=MainTableModel)

t2 = time.clock()

memf = mem_profile.memory_usage_psutil()
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Diff {} mem'.format(1024 * (memf - memb)))
print ('Took {} Seconds'.format(t2 - t1))

print(len(rows))


for row in rows:
    print(row)

print(rows[0])
