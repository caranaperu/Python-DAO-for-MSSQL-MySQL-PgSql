import Constraints
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

from Model import Model
from PersistenceErrors import PersistenceErrors


def func1(classType):
    c = classType()
    c.id_key = 100
    print(c.__dict__)



from DatabaseDelegate import DatabaseDelegate
from TransactionManager import TransactionManager
from DatabasePersistence import DatabasePersistence
import logging
import mem_profile
import time
from Constraints import Constraints

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

from abc import ABCMeta, abstractmethod

driver = 'mysql'
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
                    sql = sql + self.process_fetch_conditions(c_constraints)

                    if c_constraints.start_row:
                        sql = sql + " OFFSET " + str(c_constraints.start_row)
                    if c_constraints.end_row:
                        sql = sql + " LIMIT " + str(c_constraints.end_row - c_constraints.start_row)
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
                    if c_constraints.end_row and c_constraints.start_row == 0:
                        sql= sql+" top "+str(c_constraints.end_row)+" * from veritrade"
                    elif c_constraints.end_row-c_constraints.start_row > 0:
                        sql= sql+" * from(select *,row_number() over(order by (select null)) as row from veritrade)m "
                        sql= sql+" where row between "+str(c_constraints.start_row)+" and "+str(c_constraints.end_row)
                        sql = sql + self.process_fetch_conditions(c_constraints)
                    else:
                        sql = " * from veritrade"
                else:
                    sql = "select  * from veritrade"

        else:
            if calltest == False:
                sql = "select * from tb_maintable"

                if c_constraints:
                    sql = sql + self.process_fetch_conditions(c_constraints)

                    if c_constraints.end_row:
                        sql = sql + " LIMIT " + str(c_constraints.end_row - c_constraints.start_row)
                    if c_constraints.start_row:
                        sql = sql + " OFFSET " + str(c_constraints.start_row)
            else:
                self.fetch_definition['call_parameters']=['2294']
                sql = "fetch_results"

        print (sql)
        return sql

    def process_fetch_conditions(self, c_constraints):
        sql = ""

        if c_constraints:
            filter_fields = c_constraints.filter_fields
            if filter_fields:
                num_fields = len(filter_fields)
                sql += " where "

                for i, (field, operator) in enumerate(c_constraints.filter_fields.items()):
                    if num_fields > 1 and i >= 1:
                        sql = sql + " AND "

                    value = c_constraints.get_filter_field_value(field)
                    if value is None:
                        if operator == Constraints.FilterType.EQUAL:
                            sql = sql + field + " is null"
                        else:
                            sql = sql + field + " is not null"
                    elif (operator == Constraints.FilterType.PARTIAL or
                                  operator == Constraints.FilterType.IPARTIAL):
                        sql = sql + field + " " + self.get_filter_operator(operator) + " '%" + str(value) + "%'"
                    elif isinstance(value, str):
                        sql += field + self.get_filter_operator(operator) + "'" + str(value) + "'"
                    elif isinstance(value, bool):
                        sql += field + self.get_filter_operator(operator) + self.get_as_bool(value)
                    else:
                        sql += field + self.get_filter_operator(operator) + str(value)

            sort_fields = c_constraints.sort_fields
            if sort_fields:
                num_sort_fields = len(sort_fields)

                if num_sort_fields > 0:
                    sql += " order by "

                    for i, (field, direction) in enumerate(c_constraints.sort_fields.items()):
                        if i >= 1:
                            sql = sql + ","
                        sql = sql + field + " " + str(direction)

            return sql

    def get_filter_operator(self, filter_type):
        if driver == 'pgsql':
            return filter_type.value
        else:
            return super(DAODelegateTest, self).get_filter_operator(filter_type)

    def get_as_bool(self, bool_value):
        if driver == 'pgsql':
            if bool_value == True:
                return "'Y'"
            else:
                return "'N'"
        else:
            return super(DAODelegateTest, self).get_as_bool(bool_value)


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
constraint.start_row = 0
constraint.end_row = 100

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
    constraint.add_filter_field('anytext','Test',Constraints.FilterType.EQUAL)
    constraint.add_filter_field('id_key',40,Constraints.FilterType.GREAT_THAN_EQ)
    # Sort
    constraint.add_sort_field('id_key',Constraints.SortType.ASC)

rows = dao.fetch_records(constraint, raw_answers= True, record_type_classname=MainTableModel)

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
