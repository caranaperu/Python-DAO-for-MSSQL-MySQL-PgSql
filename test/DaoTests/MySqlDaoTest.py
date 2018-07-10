from carlib.persistence.Constraints import Constraints
from carlib.database.TransactionManager import TransactionManager
from carlib.database.DatabasePersistence import DatabasePersistence
from carlib.database.impl import MySQLBaseDelegate
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

    # retornar None si no se desea chequeo de version
    def get_version_field(self):
        return 'updated_when'


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
driver = 'mysql'

if unique_id_test:
    query_type_test = QueryType.DIRECT_CALL
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
                model.nondup = 'IsDuplicate24'
    model.anytext = 'test2333'

    trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '3306',
                                      'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})

    if query_type_test == QueryType.DIRECT_CALL:

        class DAODelegateTest(MySQLBaseDelegate):
            def __init__(self):
                MySQLBaseDelegate.__init__(self)

            def get_uid(self, cursor):
                # Es independiente del trigger, mas aun cuando aqui el trigger no puede insertar a la misma
                # tabla (Limitacion MySQL) , Para pruebas crear un trigger con un id autoincrement en otra
                # tabla.
                lastrowid = cursor.lastrowid
                print(lastrowid)
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                if not withFK:
                    return "select * from tb_maintable where id_key={}".format(key_values)
                else:
                    return "select * from tb_maintable_fk where pk_id={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                if not withFK:
                    return "insert into tb_maintable(anytext) values ('{}')".format(record_model.anytext)
                else:
                    return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}')".format(
                        record_model.anytext, record_model.fktest, record_model.nondup)

    elif query_type_test == QueryType.DIRECT_SP:
        class DAODelegateTest(MySQLBaseDelegate):
            def __init__(self):
                MySQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # El stored procedure debe hacer solo insert a la tabla que se requeire el id o el insert debe ser
                # el ultimo dentro del sp, es irrelevante si tiene selects o no ya que seran ignorados.
                # IMPORTANTE : Si se hace mas de un insert en la misma tabla el id sera del ultimo insert
                #   esto es absolutamente raro en produccion , pero valga la advertencia.
                # En el caso se agrege a otras tablas debera usarse otro type mas adecuado, la idea aqui es
                # que solo se agregue a la tabla de interes en el sp.
                #
                # El last insert id no toma en cuenta lo que suceda dentro de un trigger.
                #
                # En este caso lastrowid del cursor no retorna un valor valido.
                cursor.execute("SELECT last_insert_id();")
                lastrowid = cursor.fetchone()[0]
                print(lastrowid)
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
                    return "directspInsertTest"
                else:
                    return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}')".format(
                        record_model.anytext, record_model.fktest, record_model.nondup)

    elif query_type_test == QueryType.SP_WITH_SELECT_ID:
        class DAODelegateTest(MySQLBaseDelegate):
            def __init__(self):
                MySQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # El select que contiene el id debera ser el ultimo existente en el stored procedure de lo contrario
                # fallara, si no fuera asi y no se tiene acceso al sp puede crearse uno que envuelva
                # al primero y efectue los select en dicho orden, asi mismo el insert a la tabla que deseamos el last id
                # debera ser la ultima en ser insertada.
                # No se ve afectada por triggers.
                # Solo puede accesarse usando stored_results el cual es una extension pymysql de otra manera no funciona
                # correctamente. (Esto para el caso que existen otros selects previos al ultimo)
                lastrowid = None
                for result in cursor.stored_results():
                    lastrowid = result.fetchone()[0]
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
                    return "withSelectspInsertTest"
                else:
                    return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}')".format(
                        record_model.anytext, record_model.fktest, record_model.nondup)

    elif query_type_test == QueryType.SP_WITH_RETURN_ID:
        class DAODelegateTest(MySQLBaseDelegate):
            def __init__(self):
                MySQLBaseDelegate.__init__(self)

            def get_uid(self, cursor):
                # En mysql para retornar un valor via return y no select , solo es valido via una funcion,
                # asi mismo estas no soportan resultados de resultset , por ende aqui el resultado directo
                # es todo lo que se necesita.
                # No se ve afectada por triggers.
                lastrowid = cursor.fetchone()[0]
                print("lastrowid = {}".format(lastrowid))
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                # withReturnspInsertTest es function
                return "select withReturnspInsertTest('{}')".format(record_model.anytext)

    elif query_type_test == QueryType.SP_WITH_OUTPUT_ID:
        class DAODelegateTest(MySQLBaseDelegate):
            def __init__(self):
                MySQLBaseDelegate.__init__(self)
                self.add_definition = {'is_call': True}

            def get_uid(self, cursor):
                # En la interfase python de mysql no existe una manera standard de recoger los output params
                # pero la documentacion indica que los parametros pueden ser accesados como "@_spname_argn"
                # por ende se requiere un select para recoger el valor deseado y conocer su posicion en el
                # call.
                #
                cursor.execute("select @_withOutParamInsertTest_arg2")
                lastrowid = cursor.fetchone()[0]
                print(lastrowid)
                return lastrowid

            def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable where id_key={}".format(key_values)

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                return "withOutParamInsertTest"

    constraints = Constraints()
    constraints.add_caller_parameter(Constraints.CallerOperation.ADD, 'anytext', 1)
    if query_type_test == QueryType.SP_WITH_OUTPUT_ID:
        constraints.add_caller_parameter(Constraints.CallerOperation.ADD, '0', 2)

    daoDelegate = DAODelegateTest()

    dao = DatabasePersistence(trx, daoDelegate)

    # usamos la transacion para informar que el control es extrerno.
    if verify_dup:
        trx.start_transaction()
    ret = dao.add_record(model, reread_record=fl_reread, c_constraints=constraints)
    print(ret)
    print(model.__dict__)

    if verify_dup and ret == PersistenceErrors.DB_ERR_ALLOK:
        model.nondup = 'El segundo 32'
        ret = dao.add_record(model, reread_record=fl_reread, c_constraints=constraints)
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


    class DAODelegateTest(MySQLBaseDelegate):
        def __init__(self):
            MySQLBaseDelegate.__init__(self)

        def get_read_record_query(self, record_model, key_values, c_constraints=None, sub_operation=None):
            return "select * from tb_maintable_ckeys where main_code='{}' and main_number={} ".format(
                getattr(record_model, key_values[0]), getattr(record_model, key_values[1]))

        def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
            return "insert into tb_maintable_ckeys(main_code,main_number,anytext) values ('{}',{},'{}')".format(
                record_model.main_code, record_model.main_number, record_model.anytext)


    model = MainTableModel()
    model.main_code = '101'
    model.main_number = 120
    model.anytext = 'Soy aaaa'

    daoDelegate = DAODelegateTest()
    trx = TransactionManager(driver, {'host': '192.168.0.2', 'port': '3306',
                                      'user': 'root', 'password': 'melivane', 'database': 'py_dbtest'})
    dao = DatabasePersistence(trx, daoDelegate)

    # usamos la transacion para informar que el control es extrerno.
    ret = dao.add_record(model, reread_record=True)
    print(ret)
    print(model.__dict__)
