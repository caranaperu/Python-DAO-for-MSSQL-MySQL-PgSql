import logging
import mem_profile
import time

from carlib.database.impl.MsSQLBaseDelegate import MsSQLBaseDelegate
from carlib.persistence.Constraints import Constraints
from carlib.utils import dbutils
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.persistence.Model import Model

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

calltest = True
driver = 'mssqlpy'
# Imprtante : los drivers mssql con ODBC no soportan callproc
# y pymssql lo soporta pero no permite recoger los resultados
# con fetchall() y otras similares , por lo tanto se recomienda usar
# EXEC my_sp via el metodo execute el cual funciona perfecto en los 3 drivers.

class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.marca = None
        self.modelo = None
        self.version = None

    # retornar None si no se desea chequeo de version
    def get_pk_fields(self):
        return None


class DAODelegateTest(MsSQLBaseDelegate):
    def __init__(self):
        MsSQLBaseDelegate.__init__(self)

    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):
        if calltest:
            # pyodbc y familia NO SOPRTAN CALL PROC
            # Para msssql que ya lo soporta no implementaremos ese caso
            # ya que el standard cursor.fetchall() no funciona por ende usar
            # este metodo.
            sql = "EXEC fetch_results " + c_constraints.get_filter_field_value('marca') \
                  + "," + str(c_constraints.limit) \
                  + "," + str(c_constraints.offset)
        else:
            if c_constraints:
                sql = "select"
                if c_constraints.limit and c_constraints.offset == 0:
                    sql = sql + " top " + str(c_constraints.limit) + " marca,modelo,version from veritrade"
                elif c_constraints.limit - c_constraints.offset > 0:
                    sql = sql + " marca,modelo,version from(select top 1000000 marca,modelo,version,row_number() over(order by (select null)) as row from veritrade "
                    sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)
                    sql = sql + ")m where row between " + str(c_constraints.offset) + " and " + str(
                        c_constraints.offset + c_constraints.limit - 1)
                else:
                    sql = " marca,modelo,version from veritrade"
            else:
                sql = "select  marca,modelo,version from veritrade"
        print (sql)
        return sql


trx = TransactionManager(driver, {'dsn': 'LINUX_MSSQLSERVER', 'host': '192.168.0.2', 'port': '1433',
                                  'user': 'sa', 'password': 'Melivane100', 'database': 'veritrade'})

daoDelegate = DAODelegateTest()
dao = DatabasePersistence(trx, daoDelegate)

memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

constraint = Constraints()
constraint.offset = 100
constraint.limit = 20000

constraint.add_filter_field('importador', 'DERCO', Constraints.FilterType.IPARTIAL)
constraint.add_filter_field('marca', 'MAZDA', Constraints.FilterType.EQUAL)
# Sort
constraint.add_sort_field('pais_embarque', Constraints.SortType.ASC)

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
