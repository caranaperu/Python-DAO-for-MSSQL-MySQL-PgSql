from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.persistence.Constraints import Constraints
from carlib.database.impl import PgSQLBaseDelegate
from carlib.persistence.Model import Model
import logging
from enum import Enum

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


class QueryType(Enum):
    DIRECT_SP = 1
    SP_WITH_SELECT_ID = 2
    SP_WITH_RETURN_ID = 3
    SP_WITH_OUTPUT_ID = 4


class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.id_key = None
        self.anytext = None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('id_key',)


unique_id_test = True
driver = 'pgsql'

if unique_id_test:
    query_type_test = QueryType.SP_WITH_OUTPUT_ID
    fl_reread = True

    model = MainTableModel()
    model.anytext = 'test33'

    trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '5432', 'user': 'postgres', 'password': 'melivane',
                                      'database': 'db_pytest'})

    if query_type_test == QueryType.DIRECT_SP:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # Se supone que en este sp se agregara el registro a la tabla y se espera un solo insert
                # a la misma , de no ser asi usar otro de los metodos aceptados como :
                #   call_with_select_id , call_with_return_id o call_with_output_param_id
                #
                # Asi mismo no funcionara si en un trigger que se dispare por un after insert agrega
                # otro registro a la misma tabla , ya que el id retornado sera el del ultimo agregado.
                #
                # CURRVAL dara el ultimo id agregado a esa tabla independientemente de cual sea el origen
                # del insert el sp o un trigger after insert.
                cursor.execute("SELECT CURRVAL(pg_get_serial_sequence('tb_maintable','id_key'))")
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                # Observese que aqui se pone el nombre del stored procedure.
                # Los parametros serean extraidos del modelo a agregar.
                return "directspInsertTest"

    elif query_type_test == QueryType.SP_WITH_SELECT_ID:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # En este caso no se ve afectada por triggers ya que el id es recogido programaticamente
                # y seleccionado para ser recogido , por ende el orden posteriorde otras sentencias al insert
                # es irrelevante.
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                # Observese que aqui se pone el nombre del stored procedure.
                # Los parametros serean extraidos del modelo a agregar.
                return "withSelectspInsertTest"

    elif query_type_test == QueryType.SP_WITH_RETURN_ID:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # En este caso no se ve afectada por triggers ya que el id es recogido programaticamente
                # y seleccionado para ser recogido , por ende el orden posterior al insert es irrelevante.
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                return "withReturnspInsertTest"

    elif query_type_test == QueryType.SP_WITH_OUTPUT_ID:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # En este caso los output parameters son retornados como un solo registro en el orden declarado
                # se requerira saber cual es el que representa el idenity.
                # Dado que es programatico es irrelevante si hay trigger o selects previos , etc.
                #
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                return "withOutParamInsertTest"

    daoDelegate = DAODelegateTest()

    constraints = Constraints()
    constraints.add_caller_parameter(Constraints.CallerOperation.ADD, 'anytext', 0)

    dao = DatabasePersistence(trx, daoDelegate)

    # usamos la transacion para informar que el control es extrerno.
    ret = dao.add_record(model, reread_record=fl_reread, c_constraints=constraints)
    print(ret)
    print(model.__dict__)
