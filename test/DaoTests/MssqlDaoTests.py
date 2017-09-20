
import sys
sys.path.insert(0, '/home/carana/PycharmProjects/test')

from TransactionManager import TransactionManager
from DAOBase import DAOBase
from DAOErrorConstants import DAOErrorConstants
from DAODelegate import DAODelegate
from BaseModel import BaseModel
import logging
import random
import string

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

class MainTableModelWithFK(BaseModel):
    def __init__(self):
        BaseModel.__init__(self)
        self.pk_id = None # type: int
        self.anytext = None # type: str
        self.fktest = None
        self.nondup = None

    def is_UID_pk(self):
        return True

    def get_pk_fields(self):
        None

if __name__ == "__main__":

    class MSDAODelegate(DAODelegate):
        def __init__(self, addDef=None):
            DAODelegate.__init__(self, addDef)

        def is_duplicate_key_error(self, error_msg):
            # type: (str) -> bool
            if (error_msg.find("DB-Lib error message 2627, severity 14") >= 0 or error_msg.find("DB-Lib error message 2601, severity 14") >= 0
                or error_msg.find('Violation of UNIQUE KEY constraint') >= 0):
                return True
            return False

        def is_foreign_key_error(self, error_msg):
            # type: (str) -> bool

            # El primer chequeo es para odbc drivers , el otro es para pymssql
            if ((error_msg.find("DB-Lib error message 547, severity 16") >= 0 and error_msg.find("FOREIGN KEY constraint") >= 0)
                or error_msg.find("conflicted with the FOREIGN KEY constraint") >= 0):
                return True
            return False

    unique_id_test = False
    driver = 'mssql'

    if unique_id_test:
        query_type_test = DAOBase.QueryType.DIRECT_CALL
        fl_reread=True
        withFK = True
        verify_dup = False


        if not withFK:
            model = MainTableModel()
        else:
            if query_type_test != DAOBase.QueryType.DIRECT_CALL:
                raise ValueError('No es necesaria esta prueba basta el caso DIRECT_CALL')
            else:
                model = MainTableModelWithFK()
                model.fktest = 1
                model.nondup = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                if verify_dup == True:
                    model.nondup ='IsDuplicate11'
        model.anytext = 'test'


        trx = TransactionManager(driver,{'dsn': 'MSSQLServer', 'host': '192.168.0.9','port':'1433',
                                        'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})

        if query_type_test == DAOBase.QueryType.DIRECT_CALL:

            class DAODelegateTest(MSDAODelegate):
                def __init__(self, addDef=None):
                    MSDAODelegate.__init__(self, addDef)

                def get_UID(self, cursor):
                    # Es irrelevante si un trigger inserta a la misma tabla.
                    cursor.execute("select SCOPE_IDENTITY();")
                    lastrowid = cursor.fetchone()[0]
                    print("lastrowid = {}".format(lastrowid))
                    return lastrowid

                def get_read_record_query(self, record_model, pk_keys, c_constraints=None, sub_operation=None):
                    if not withFK:
                        return "select * from tb_maintable where pk_id={}".format(pk_keys)
                    else:
                        return "select * from tb_maintable_fk where pk_id={}".format(pk_keys)

                def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                    if not withFK:
                        return "insert into tb_maintable(anytext) values ('{}')".format(record_model.anytext)
                    else:
                        if record_model.nondup is None:
                            return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},null)".format(record_model.anytext,record_model.fktest)
                        else:
                            return "insert into tb_maintable_fk(anytext,fktest,nondup) values ('{}',{},'{}')".format(record_model.anytext,record_model.fktest,record_model.nondup)


        elif query_type_test == DAOBase.QueryType.DIRECT_SP:
            raise Exception('Unsupported , cant get LAST ID for DIRECT_SP...')
        elif query_type_test == DAOBase.QueryType.SP_WITH_SELECT_ID:
            class DAODelegateTest(MSDAODelegate):
                def __init__(self, addDef=None):
                    MSDAODelegate.__init__(self, addDef)

                def get_UID(self, cursor):
                    # El select que contiene el id debera estar antes que cualquier otro select existente en el
                    # stored procedure o ser el unico, si no fuera asi y no se tiene acceso al sp puede crearse
                    # uno que envuelva al primero y efectue los select en dicho orden.
                    # No se ve afectada por triggers ya que el id es recogido programaticamente y seleccionado
                    # para ser recogido , por ende el orden posterior al insert es irrelevante.
                    # Los sp no pueden tener el set count off !!!!
                    lastrowid = cursor.fetchone()[0]
                    print("lastrowid = {}".format(lastrowid))
                    return lastrowid

                def get_read_record_query(self, record_model, pk_keys, c_constraints=None, sub_operation=None):
                    return "select * from tb_maintable where pk_id={}".format(pk_keys)

                def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                    return "set nocount on;EXEC withSelectspInsertTest '{}';".format(record_model.anytext)

        elif query_type_test == DAOBase.QueryType.SP_WITH_RETURN_ID:
            class DAODelegateTest(MSDAODelegate):
                def __init__(self, addDef=None):
                    MSDAODelegate.__init__(self, addDef)

                def get_UID(self, cursor):
                    # Es irrelevante si existen selects antes que el return , siempre se r//ecogera
                    # como id el ultimo resultado, por ende si el ultimo select no es el id no
                    # funcionara.
                    # No se ve afectada por triggers ya que el id es recogido programaticamente y seleccionado
                    # para ser recogido , por ende el orden posterior al insert es irrelevante.
                    # Los sp no pueden tener el set count off !!!!
                    lastrowid = cursor.fetchone()[0]
                    while cursor.nextset():
                        lastrowid = cursor.fetchone()[0]
                    print("lastrowid = {}".format(lastrowid))
                    return lastrowid

                def get_read_record_query(self, record_model, pk_keys, c_constraints=None, sub_operation=None):
                    return "select * from tb_maintable where pk_id={}".format(pk_keys)

                def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                    return "set nocount on;declare @id int;EXEC @id = withReturnspInsertTest '{}';select @id;".format(record_model.anytext)

        elif query_type_test == DAOBase.QueryType.SP_WITH_OUTPUT_ID:
            class DAODelegateTest(MSDAODelegate):
                def __init__(self, addDef=None):
                    MSDAODelegate.__init__(self, addDef)

                def get_UID(self, cursor):
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

                def get_read_record_query(self, record_model, pk_keys, c_constraints=None, sub_operation=None):
                    return "select * from tb_maintable where pk_id={}".format(pk_keys)

                def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                    return "set nocount on;declare @id int;declare @pp varchar(10);EXEC withOutParamInsertTest '{}',@id output,@pp output;select @pp;select @id;".format(record_model.anytext)

        daoDelegate = DAODelegateTest()

        #daoDelegate.set_add_definition()
        #daoDelegate.set_read_definition()

        dao = DAOBase(trx, daoDelegate)

        # usamos la transacion para informar que el control es extrerno.
        trx.start_transaction()
        ret = dao.add_record(model,query_type=query_type_test,rereadRecord=fl_reread)
        print(ret)
        print(model.__dict__)

        if verify_dup == True and ret == DAOErrorConstants.DB_ERR_ALLOK:
            model.nondup = 'El segundo 10'
            ret = dao.add_record(model,query_type=query_type_test,rereadRecord=fl_reread)
            print(ret)
            print(model.__dict__)
        # cerreamos la transacion global
        trx.end_transaction()
    else:
        class MainTableModel(BaseModel):
            def __init__(self):
                BaseModel.__init__(self)
                self.main_code = None # type: int
                self.main_number = None # type: int
                self.anytext = None # type: str

            def is_UID_pk(self):
                return False

            def get_pk_fields(self):
                return ('main_code','main_number')

        class DAODelegateTest(MSDAODelegate):
            def __init__(self, addDef=None):
                MSDAODelegate.__init__(self, addDef)

            def get_read_record_query(self, record_model, pk_keys, c_constraints=None, sub_operation=None):
                return "select * from tb_maintable_ckeys where main_code='{}' and main_number={} ".format(getattr(record_model,pk_keys[0]),getattr(record_model,pk_keys[1]))

            def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
                return "insert into tb_maintable_ckeys(main_code,main_number,anytext) values ('{}',{},'{}')".format(record_model.main_code,record_model.main_number,record_model.anytext)

        model = MainTableModel()
        model.main_code = '001'
        model.main_number = 1
        model.anytext = 'Soy 0001'

        daoDelegate = DAODelegateTest()
        trx = TransactionManager(driver,{'dsn': 'MSSQLServer', 'host': '192.168.0.9','port':'1433',
                                        'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})
        dao = DAOBase(trx, daoDelegate)


        # usamos la transacion para informar que el control es extrerno.
        ret = dao.add_record(model,query_type=None,rereadRecord=True)
        print(ret)
        print(model.__dict__)