import logging
import mem_profile
import time
from carlib.persistence.Constraints import Constraints
from carlib.utils import dbutils
from carlib.database.impl import PgSQLBaseDelegate
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.persistence.Model import Model
from carlib.utils.mdlvalidators import *

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)



class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.__c_bpartner_id = None
        self.__c_groupdoc_id = None
        self.__docaction = None
        self.issotrx = None

    @property
    def c_bpartner_id(self):
        print('paso')
        return self.__c_bpartner_id

    @c_bpartner_id.setter
    @fv_num_minmax(0,1009999)
    def c_bpartner_id(self, partner_id):
        print('paso 2')
        self.__c_bpartner_id =partner_id

    @property
    def c_groupdoc_id(self):
        print('paso xx')
        return self.__c_groupdoc_id

    @c_groupdoc_id.setter
    @fv_less_than_equal(1000000000)
    def c_groupdoc_id(self, groupdoc_id):
        print('paso xx2')
        self.__c_groupdoc_id = groupdoc_id

    @property
    def docaction(self):
        print('paso xxx')
        return self.__docaction

    @docaction.setter
    @fv_len(1,2,allow_none=False)
    @fv_allow_null()
    def docaction(self, docaction):
        print('paso xx3')
        self.__docaction = docaction

    def get_pk_fields(self):
        return None


class DAODelegateTest(PgSQLBaseDelegate):
    def __init__(self):
        PgSQLBaseDelegate.__init__(self)

    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):
        sql = "select c_bpartner_id,c_groupdoc_id,docaction,issotrx from c_invoice"
        if c_constraints:
            sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)

            if c_constraints.offset:
                sql = sql + " OFFSET " + str(c_constraints.offset)
            if c_constraints.limit:
                sql = sql + " LIMIT " + str(c_constraints.limit)

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

constraint.offset = 100
constraint.limit = 500

constraint.add_filter_field('c_groupdoc_id', None, Constraints.FilterType.NO_EQUAL)
constraint.add_filter_field('docaction', 'cl', Constraints.FilterType.IPARTIAL)
constraint.add_filter_field('issotrx', 'Y', Constraints.FilterType.EQUAL)
constraint.add_filter_field('c_bpartner_id', 1009903, Constraints.FilterType.NO_EQUAL)

constraint.add_sort_field('c_groupdoc_id', Constraints.SortType.ASC)
constraint.add_sort_field('c_bpartner_id', Constraints.SortType.DESC)


rows = dao.fetch_records(constraint, raw_answers=False, record_type_classname=MainTableModel)

t2 = time.clock()

memf = mem_profile.memory_usage_psutil()
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Diff {} mem'.format(1024 * (memf - memb)))
print ('Took {} Seconds'.format(t2 - t1))

print(len(rows))

#for row in rows:
#    if isinstance(row, MainTableModel):
#        print(row.__dict__)
#    else:
#        print(row)

