# some_file.py
import sys
sys.path.insert(0, '/home/carana/PycharmProjects/test')

from TransactionManager import TransactionManager
from DAOBase import DAOBase

class MssqlDaoTest(DAOBase):

    def __init__(self, trx_mgr):
        # type: (TransactionManager) -> None
        """Initialize  variables."""

        DAOBase.__init__(self, trx_mgr)

    def get_read_record_query(self, key_value, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        return "select factura_id,factura_fecha,xmin,autoi,tb_factura_item_id from tb_factura4 where autoi = {}".format(key_value)

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (Any,DAOConstraints,str) ->str
        #return "insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values ({},'{}','{}',{})".format(record_model.factura_id,record_model.factura_fecha,record_model.name,record_model.tb_factura_item_id)
        return "insert into tb_maintable(anytext) values ('{}')".format(record_model.anytext)

    def get_UID(self, cursor, query_type):
        # type: (Cursor,QueryType) -> int
        if query_type == "directcall":
            # Es irrelevante si un trigger inserta a la misma tabla.
            cursor.execute("select SCOPE_IDENTITY();")
            lastrowid = cursor.fetchone()[0]
            print("lastrowid = {}".format(lastrowid))
        elif query_type == "directsp":
            cursor.execute("select SCOPE_IDENTITY();")
            lastrowid = cursor.fetchone()[0]
            print("lastrowid = {}".format(lastrowid))
        elif query_type == "call_with_select_id":
            # El select que contiene el id debera estar antes que cualquier otro select existente en el
            # stored procedure o ser el unico, si no fuera asi y no se tiene acceso al sp puede crearse
            # uno que envuelva al primero y efectue los select en dicho orden.
            # No se ve afectada por triggers ya que el id es recogido programaticamente y seleccionado
            # para ser recogido , por ende el orden posterior al insert es irrelevante.
            # Los sp no pueden tener el set count off !!!!
            lastrowid = cursor.fetchone()[0]
            print("lastrowid = {}".format(lastrowid))
        elif query_type == "call_with_return_id":
            # Es irrelevante si existen selects antes que el return , siempre se recogera
            # como id el ultimo resultado, por ende si el ultimo select no es el id no
            # funcionara.
            # No se ve afectada por triggers ya que el id es recogido programaticamente y seleccionado
            # para ser recogido , por ende el orden posterior al insert es irrelevante.
            # Los sp no pueden tener el set count off !!!!
            lastrowid = cursor.fetchone()[0]
            while cursor.nextset():
                lastrowid = cursor.fetchone()[0]
            print("lastrowid = {}".format(lastrowid))
        elif query_type == "call_with_output_param_id":
            # EL controlador pyodbc o pypyodbc no soportan output parameters , por ende se tiene que simular
            # y el mayor problema es que si el stored procedure a la vez retorna algun select al menos
            # estos resultados vendran primero y al final el output parameter sera recogido , por ende
            # se recorreran todos los resultados y el ultimo encontrado sera el id.
            # Para que esto funcione el stored procedure sera modificado antes de ejecutarse a la siguiente
            # manera:
            #   set nocount on;declare @out_param int;EXEC my_sp_with_out_params param1,param2,param...,@out_param output;select @out_param
            # En el caso que existan mas de un output parameter , EL ULTIMO EN SER RECOGIDO debe ser el UNIQUE ID.
            #
            # Los sp no pueden tener el set count off !!!!
            #
            lastrowid = cursor.fetchone()[0]
            while cursor.nextset():
                lastrowid = cursor.fetchone()[0]
            print("lastrowid = {}".format(lastrowid))
        return lastrowid

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


from BaseModel import BaseModel
import logging

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

class MainTableModel(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.pk_id = None # type: int
        self.anytext = None # type: str

    def is_UID_pk(self):
        return True

    def get_pk_fields(self):
        None

if __name__ == "__main__":
    trx = TransactionManager('mssqlpy',{'dsn': 'MSSQLServer', 'host': '192.168.0.9',
                                       'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})
    dao = MssqlDaoTest(trx)
    model = MainTableModel()
    model.anytext = 'test'

    ret = dao.add_record(model)
    print(ret)
