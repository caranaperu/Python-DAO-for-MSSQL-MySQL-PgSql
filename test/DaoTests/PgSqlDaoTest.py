from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import PgSQLBaseDelegate
from carlib.persistence.PersistenceErrors import PersistenceErrors
from carlib.persistence.Model import Model
import logging
import random
import string
from enum import Enum

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


class QueryType(Enum):
    DIRECT_CALL = 0
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


class MainTableModelWithFK(Model):
    def __init__(self):
        Model.__init__(self)
        self.pk_id = None
        self.anytext = None
        self.fktest = None
        self.nondup = None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return None


unique_id_test = True
driver = 'pgsql'

if unique_id_test:
    query_type_test = QueryType.DIRECT_SP
    fl_reread = True
    withFK = False
    verify_dup = False

    if not withFK:
        model = MainTableModel()
    else:
        if query_type_test != QueryType.DIRECT_CALL:
            raise ValueError('No es necesaria esta prueba basta el caso DIRECT_CALL')
        else:
            model = MainTableModelWithFK()
            model.fktest = 1  # 1 - es ok , 2- genera error de foreign key
            model.nondup = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            if verify_dup:
                model.nondup = 'IsDuplicate25'
    model.anytext = 'test'

    trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '5432', 'user': 'postgres', 'password': 'melivane',
                                      'database': 'db_pytest'})

    if query_type_test == QueryType.DIRECT_CALL:

        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)

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
                if not withFK:
                    return "select * from tb_maintable where id_key={}".format(key_values)
                else:
                    return "select * from tb_maintable_fk where pk_id={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                if not withFK:
                    return "insert into tb_maintable(id_key,anytext) values (DEFAULT,'{}') returning id_key".format(
                        record_model.anytext)
                else:
                    return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}') returning pk_id".format(
                        record_model.anytext, record_model.fktest, record_model.nondup)

    elif query_type_test == QueryType.DIRECT_SP:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)

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
                if not withFK:
                    return "select * from tb_maintable where id_key={}".format(key_values)
                else:
                    return "select * from tb_maintable_fk where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                if not withFK:
                    # Observese que aqui se pone el nombre del stored procedure.
                    # Los parametros serean extraidos del modelo a agregar.
                    return "select directspInsertTest('{}');".format(record_model.anytext)
                else:
                    return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}')".format(
                        record_model.anytext, record_model.fktest, record_model.nondup)

    elif query_type_test == QueryType.SP_WITH_SELECT_ID:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)

            def get_uid(self, cursor):
                # En este caso no se ve afectada por triggers ya que el id es recogido programaticamente
                # y seleccionado para ser recogido , por ende el orden posteriorde otras sentencias al insert
                # es irrelevante.
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                if not withFK:
                    return "select * from tb_maintable where id_key={}".format(key_values)
                else:
                    return "select * from tb_maintable_fk where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                if not withFK:
                    # Observese que aqui se pone el nombre del stored procedure.
                    # Los parametros serean extraidos del modelo a agregar.
                    return "select withSelectspInsertTest('{}');".format(record_model.anytext)
                else:
                    return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}')".format(
                        record_model.anytext, record_model.fktest, record_model.nondup)

    elif query_type_test == QueryType.SP_WITH_RETURN_ID:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)

            def get_uid(self, cursor):
                # En este caso no se ve afectada por triggers ya que el id es recogido programaticamente
                # y seleccionado para ser recogido , por ende el orden posterior al insert es irrelevante.
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                return "select withReturnspInsertTest('{}');".format(record_model.anytext)

    elif query_type_test == QueryType.SP_WITH_OUTPUT_ID:
        class DAODelegateTest(PgSQLBaseDelegate):
            def __init__(self):
                PgSQLBaseDelegate.__init__(self)

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
                return "select * from withOutParamInsertTest('{}');".format(record_model.anytext)

    daoDelegate = DAODelegateTest()

    dao = DatabasePersistence(trx, daoDelegate)

    # usamos la transacion para informar que el control es extrerno.
    if verify_dup:
        trx.start_transaction()
    ret = dao.add_record(model, reread_record=fl_reread)
    print(ret)
    print(model.__dict__)

    if verify_dup and ret == PersistenceErrors.DB_ERR_ALLOK:
        model.nondup = 'El segundo 25'
        ret = dao.add_record(model, reread_record=fl_reread)
        print(ret)
        print(model.__dict__)

    # cerreamos la transacion global
    trx.end_transaction()

else:
    class MainTableModel(Model):
        def __init__(self):
            Model.__init__(self)
            self.main_code = None
            self.main_number = None
            self.anytext = None

        def is_pk_uid(self):
            return False

        def get_pk_fields(self):
            return ('main_code', 'main_number')


    class DAODelegateTest(PgSQLBaseDelegate):
        def __init__(self):
            PgSQLBaseDelegate.__init__(self)

        def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
            return "select * from tb_maintable_ckeys where main_code='{}' and main_number={} ".format(
                getattr(record_model, key_values[0]), getattr(record_model, key_values[1]))

        def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
            return "insert into tb_maintable_ckeys(main_code,main_number,anytext) values ('{}',{},'{}')".format(
                record_model.main_code, record_model.main_number, record_model.anytext)


    model = MainTableModel()
    model.main_code = '011'
    model.main_number = 10
    model.anytext = 'Soy 0010'

    daoDelegate = DAODelegateTest()
    trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '5432', 'user': 'postgres', 'password': 'melivane',
                                      'database': 'db_pytest'})
    dao = DatabasePersistence(trx, daoDelegate)

    # usamos la transacion para informar que el control es extrerno.
    ret = dao.add_record(model, reread_record=True)
    print(ret)
    print(model.__dict__)
