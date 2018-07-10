import logging
import mem_profile
import time

from carlib.utils import dbutils
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.persistence.Model import Model
from carlib.database.impl.MySQLBaseDelegate import MySQLBaseDelegate
from carlib.persistence.Constraints import Constraints

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

calltest = False


class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.id_key = None
        self.anytext = None

    def get_pk_fields(self):
        return None


class DAODelegateTest(MySQLBaseDelegate):
    def __init__(self):
        MySQLBaseDelegate.__init__(self)
        if calltest:
            self.fetch_definition = {'is_call': True}

    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):
        if calltest is False:
            sql = "select * from tb_maintable"
            if c_constraints:
                sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)

                if c_constraints.limit:
                    sql = sql + " LIMIT " + str(c_constraints.limit)
                if c_constraints.offset:
                    sql = sql + " OFFSET " + str(c_constraints.offset)
        else:
            sql = "fetch_results"
        print (sql)
        return sql


trx = TransactionManager('mysql', {'host': '192.168.0.2', 'port': '3306',
                                   'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})

daoDelegate = DAODelegateTest()
dao = DatabasePersistence(trx, daoDelegate)

memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

constraint = Constraints()
constraint.offset = 10
constraint.limit = 20

if not calltest:
    constraint.add_filter_field('id_key', 0, Constraints.FilterType.GREAT_THAN_EQ)
    constraint.add_filter_field('anytext', 'Test', Constraints.FilterType.EQUAL)
    # Sort
    constraint.add_sort_field('id_key', Constraints.SortType.ASC)
else:
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 'Test', 0)
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 25, 1)
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 10, 2)

rows = dao.fetch_records(constraint, raw_answers=False, record_type_classname=MainTableModel)

t2 = time.clock()

memf = mem_profile.memory_usage_psutil()
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Diff {} mem'.format(1024 * (memf - memb)))
print ('Took {} Seconds'.format(t2 - t1))

print(len(rows))

for row in rows:
    print(row)

if isinstance(rows[0], MainTableModel):
    print(rows[0].__dict__)
else:
    print(rows[0])
