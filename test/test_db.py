

import mem_profile
import time
from DbDriverFactory import DbDriverFactory
import logging

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

#'''
xx = DbDriverFactory.get_db_driver('mysql')

memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

conn = xx.connect(host='localhost', user='root',
                  password='melivane', database='test')
cur = conn.cursor()
try:
    cur.execute("""SELECT * from tb_atletas""")
    # print(cur.description)
    print(cur.rowcount)
    field_names = [i[0] for i in cur.description]
    print(field_names)
    for row in cur.fetchall():
        print("Record\n")
        print(row)
        for i in xrange(len(cur.description)):
            print("FieldName: %-50s Value: %-50s" %
                  (cur.description[i][0], row[i]))

        print("=================\n")
    print(cur.rowcount)
finally:
    cur.close()


t2 = time.clock()

memf = mem_profile.memory_usage_psutil()
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Diff {} mem'.format(1024 * (memf - memb)))
print ('Took {} Seconds'.format(t2 - t1))
#'''
xx = DbDriverFactory.get_db_driver('pgsql')
memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

conn = xx.connect(host='192.168.0.5', user='postgres',
                  password='melivane', database='db_atletismo')
cur = conn.cursor()
try:
    cur.execute("""SELECT * from tb_atletas limit 10""")
    # print(cur.description)
    print(cur.rowcount)
    field_names = [i[0] for i in cur.description]
    print(field_names)

    for row in cur.fetchall():
        print("Record\n")
        print(row)
        for i in xrange(len(cur.description)):
            print("FieldName: %-50s Value: %-50s" %
                  (cur.description[i][0], row[i]))

        print("=================\n")
finally:
    cur.close()

t2 = time.clock()

memf = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Took {} Seconds'.format(t2 - t1))

# MSSQL SERVER
memf = mem_profile.memory_usage_psutil()
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Diff {} mem'.format(1024 * (memf - memb)))
print ('Took {} Seconds'.format(t2 - t1))
#'''
xx = DbDriverFactory.get_db_driver('mssql')
memb = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
t1 = time.clock()

conn = xx.connect(host='192.168.0.9', user='sa',
                  password='melivane', database='veritrade')
cur = conn.cursor()
try:
    cur.execute("""SELECT  TOP 1 * from veritrade where ano_reporte=2017""")
    # print(cur.description)
    print(cur.rowcount)
    field_names = [i[0] for i in cur.description]
    print(field_names)

    for row in cur.fetchall():
        print("Record\n")
        print(row)
        for i in xrange(len(cur.description)):
            print("FieldName: %-50s Value: %-50s" %
                  (cur.description[i][0], row[i]))

        print("=================\n")
        print(cur.rowcount)
finally:
    cur.close()

t2 = time.clock()

import sys
memf = mem_profile.memory_usage_psutil()
print ('Memory (Before): {}Mb'.format(memb))
print ('Memory (After) : {}Mb'.format(memf))
print ('Diff {} mem'.format(memf - memb))
print ('Took {} Seconds'.format(t2 - t1))


conn = xx.connect(host='192.168.0.9', user='sa',
                  password='melivane', database='pytest')
cur = conn.cursor()
try:
    cur.execute(
        """insert into tb_factura (factura_id,factura_fecha) values(2,'2016-01-01')""")
    print(cur.rowcount)
    cur.execute("""insert into tb_factura_items ([tb_factura_item_id]
        ,[tb_facura_id]
        ,[tb_factura_cod]
        ,[tb_factura_qty]
        ,[tb_factura_val]) values(1,1,'test',1,100.00)""")
    print(cur.rowcount)
    conn.commit()
except:
    print("Unexpected error:", sys.exc_info()[0])
    conn.rollback()
finally:
    cur.close()
    conn.close()


from BaseModel import BaseModel
from DAOBase import DAOBase
from TransactionManager import TransactionManager


class SqlTestModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.marca = None  # type: str
        self.modelo = None  # type: str
        self.version = None  # type: str
        self.fecha_dua = None  # type: date

    def get_unique_id(self):
        return None


class DAOBaseMSSQL(DAOBase):
    def get_read_record_query(self, key_value, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        return "select marca,modelo,version,fecha_dua from veritrade where CHASSISDATA ='JTFSS22P4H0158420' and ANO_NACIONALIZACION = 2017"

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        return ""

    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        if (error_msg.find("1052 (23000)") >= 0):
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool
        return False

class DAOBasePGSQL(DAOBase):
    def get_read_record_query(self, key_value, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        return "select id,name,code,create_date from account_account where code ='103000'"

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        return ""

    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        if (error_msg.find("1052 (23000)") >= 0):
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool
        return False

class DAOBaseMYSQL(DAOBase):
    def get_read_record_query(self, key_value, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        if isinstance(key_value,dict):
            return "SELECT * from tb_atletas where id_atletas={}".format(key_value["id_atletas"])
        return "SELECT * from tb_atletas where id_atletas={}".format(key_value)

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (BaseModel,DAOConstraints,str) ->str
        return "insert into tb_atletas(id_atletas,tb_atletas_nombres,id_referenced) values ({},'{}',{})".format(record_model.id_atletas,record_model.tb_atletas_nombres,record_model.id_referenced)

    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        if (error_msg.find("1062 (23000):") >= 0):
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool
        if error_msg.find("1452 (23000):") >= 0 and error_msg.find("foreign key constraint fails") >= 0:
            return True
        return False


testModel = SqlTestModel()

trx = TransactionManager('mssql', {'host': '192.168.0.9', 'port': '1433',
                                   'user': 'sa', 'password': 'melivane', 'database': 'veritrade'})

dao = DAOBaseMSSQL(trx)

# print(dao.read_record("sss","ssssss"))
print(dao.read_record("testModel", testModel))
print("======TestMODEL===============")
print(testModel.__dict__)
print("==============================")

#t = testModel.fecha_dua.timetuple()
# for i in t:
#     print i

#trx = TransactionManager('mssql',{'host': '192.168.0.9', 'user': 'sa', 'password': 'melivane', 'database': 'veritrade' })
trx.start_transaction()
cur = trx.get_transaction_cursor()
print(cur)
cur = None
trx.start_transaction()
cur2 = trx.get_transaction_cursor()
print(cur2)
trx.end_transaction()
trx.end_transaction()
trx.end_transaction()

drv = trx.db_driver
print(drv)
drv = None
drv2 = trx.db_driver
print(drv2)


class PgSQLTestModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.id = None  # type: str
        self.name = None  # type: str
        self.code = None  # type: str
        self.create_date = None  # type: date

    def get_unique_id(self):
        return self.id

class MySQLTestModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.id_atletas = None  # type: int
        self.tb_atletas_nombres = None  # type: str
        self.id_referenced = None

    def get_unique_id(self):
        return self.id_atletas


test2Model = PgSQLTestModel()
trx = TransactionManager('pgsql', {'host': '192.168.0.5', 'port': '5432',
                                   'user': 'postgres', 'password': 'melivane', 'database': 'odoo_enterprise'})
# print(dao.read_record("sss","ssssss"))
dao = DAOBasePGSQL(trx)

print(dao.read_record("testModel", test2Model))
print("======TestMODEL===============")
print(test2Model.__dict__)
print("==============================")

t = test2Model.create_date.timetuple()
for i in t:
    print(i)


test3Model = MySQLTestModel()

trx = TransactionManager('mysql', {'host': 'localhost', 'port': '3306',
                                   'user': 'root', 'password': 'melivane', 'database': 'test'})
# print(dao.read_record("sss","ssssss"))
dao = DAOBaseMYSQL(trx)

print(dao.read_record({"id_atletas": 0 , "xxx": "zzzzz"}, test3Model))
print("======TestMODEL===============")
print(test3Model.__dict__)
print("==============================")


trx2 = TransactionManager('mysql', {'host': 'localhost', 'port': '3306',
                                   'user': 'root', 'password': 'melivane', 'database': 'test'})
# print(dao.read_record("sss","ssssss"))
dao2 = DAOBaseMYSQL(trx2)

test3Model.id_atletas=117
test3Model.tb_atletas_nombres="Soy usuario de test 117"
test3Model.id_referenced = 1

print(dao2.add_record(test3Model))

print("======Test 3 MODEL===============")
print(test3Model.__dict__)
print("==============================")

# =======================================================================================================
class DAOBaseMSSQL2(DAOBase):
    def get_read_record_query(self, key_value, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        return "select factura_id,factura_fecha,xmin,autoi,tb_factura_item_id from tb_factura4 where autoi = {}".format(key_value)

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        #return "insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values ({},'{}','{}',{})".format(record_model.factura_id,record_model.factura_fecha,record_model.name,record_model.tb_factura_item_id)
        return "EXEC uspaddFactura4 {},'{}'".format(record_model.factura_id,record_model.name)

    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        if error_msg.find("DB-Lib error message 2627, severity 14") >= 0 or error_msg.find("DB-Lib error message 2601, severity 14") >= 0:
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool
        if error_msg.find("DB-Lib error message 547, severity 16") >= 0 and error_msg.find("FOREIGN KEY constraint") >= 0:
            return True
        return False

class SqlTestModel2(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.factura_id = None  # type: int
        self.factura_fecha = None  # type: date
        self.xmin = None  # type: Any
        self.autoi = None
        self.tb_factura_item_id = None

    def get_unique_id(self):
        return self.autoi
        #return None

    def is_pk_identity(self):
        return True

print("\n***************** Test MSSQL *****************")
testModel = SqlTestModel2()

trxmsql = TransactionManager('mssql', {'host': '192.168.0.9', 'port': '1433',
                                   'user': 'sa', 'password': 'melivane', 'database': 'pytest'})

dao = DAOBaseMSSQL2(trxmsql)
print(dao.read_record(22,testModel))
print(testModel.__dict__)

testModel.factura_id=363
testModel.factura_fecha="2018-01-01"
testModel.xmin = None
testModel.name = "car363"
testModel.autoi = None
testModel.tb_factura_item_id = 2

print(dao.add_record(testModel,DAOBaseMSSQL.QueryType.SP_CALL))
print(testModel.__dict__)
