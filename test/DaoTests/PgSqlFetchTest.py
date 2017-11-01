import logging
import mem_profile
import time
from carlib.persistence.Constraints import Constraints
from carlib.utils import dbutils
from carlib.database.impl import PgSQLBaseDelegate
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.persistence.Model import Model

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

calltest = False


class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.c_bpartner_id = None
        self.c_groupdoc_id = None
        self.docaction = None
        self.issotrx = None

    def get_pk_fields(self):
        return None


class DAODelegateTest(PgSQLBaseDelegate):
    def __init__(self):
        PgSQLBaseDelegate.__init__(self)
        if calltest:
            self.fetch_definition = {'is_call': True}

    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):
        if calltest is False:
            sql = "select c_bpartner_id,c_groupdoc_id,docaction,issotrx from c_invoice"
            if c_constraints:
                sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)

                if c_constraints.offset:
                    sql = sql + " OFFSET " + str(c_constraints.offset)
                if c_constraints.limit:
                    sql = sql + " LIMIT " + str(c_constraints.limit)
        else:
            sql = "fetch_results"
        print (sql)
        return sql


trx = TransactionManager('pgsql', {'host': '192.168.0.5', 'port': '5432', 'user': 'postgres', 'password': 'melivane',
                                   'database': 'xendra'})

daoDelegate = DAODelegateTest()
dao = DatabasePersistence(trx, daoDelegate)

memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

constraint = Constraints()

if not calltest:
    constraint.offset = 100
    constraint.limit = 500

    constraint.add_filter_field('c_groupdoc_id', None, Constraints.FilterType.NO_EQUAL)
    constraint.add_filter_field('docaction', 'cl', Constraints.FilterType.IPARTIAL)
    constraint.add_filter_field('issotrx', 'Y', Constraints.FilterType.EQUAL)
    constraint.add_filter_field('c_bpartner_id', 1009790, Constraints.FilterType.NO_EQUAL)

    constraint.add_sort_field('c_groupdoc_id', Constraints.SortType.ASC)
    constraint.add_sort_field('c_bpartner_id', Constraints.SortType.DESC)
else:
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 150, 2)
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 0, 3)
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 'Y', 1)
    constraint.add_caller_parameter(Constraints.CallerOperation.FETCH, 1009790, 0)

rows = dao.fetch_records(constraint, raw_answers=True, record_type_classname=MainTableModel)

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
