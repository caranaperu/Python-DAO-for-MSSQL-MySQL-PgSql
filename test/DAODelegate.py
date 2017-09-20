from abc import ABCMeta, abstractmethod
from DAOConstraints import DAOConstraints
from BaseModel import BaseModel

class DAODelegate(object):
    """Clase abstracta que define las operaciones especificas para cada DAO."""

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.__addDef = {'isCall': False, 'callParameters': None}
        self.__readDef = {'isCall': False, 'callParameters': None}

    def set_add_definition(self, isCall, callParameters):
        self.__addDef = {'isCall': isCall, 'callParameters': callParameters}

    def set_read_definition(self, isCall, callParameters):
        self.__readDef = {'isCall': isCall, 'callParameters': callParameters}


    def get_read_record_query(self, record_model, pk_keys, c_constraints=None, sub_operation=None):
        # type: (BaseModel,DAOConstraints,str,(Dict | Any)) -> str
        return None

    def get_add_record_query(self, record_model, c_constraints=None, sub_operation=None):
        # type: (BaseModel,DAOConstraints,str) -> str
        return None

    def execute_add_SQL(self, cursor, record_model, c_constraints=None, sub_operation=None):
        # type: (Cursor, BaseModel,DAOConstraints, str) -> None
        if self.__addDef:
            sql_sentence = self.get_add_record_query(record_model, c_constraints, sub_operation);
            if self.__addDef['isCall']:
                if self.__addDef['callParameters']:
                    params =[]
                    for field in self.__addDef['callParameters']:
                        if hasattr(record_model, field):
                            params.append(getattr(record_model,field))
                    cursor.callproc(sql_sentence, params)
                else:
                    cursor.callproc(sql_sentence)
            else:
                cursor.execute(sql_sentence)

    def execute_read_SQL(self, cursor, record_model, pk_keys, c_constraints=None, sub_operation=None):
        # type: (Cursor, BaseModel, (Dict | int), DAOConstraints, str) -> None
        if self.__readDef:
            sql_sentence = self.get_read_record_query(record_model, pk_keys, c_constraints, sub_operation);
            if self.__readDef['isCall']:
                if self.__readDef['callParameters']:
                    params =[]
                    for field in self.__readDef['callParameters']:
                        if hasattr(record_model, field):
                            params.append(getattr(record_model,field))
                    cursor.callproc(sql_sentence, params)
                else:
                    cursor.callproc(sql_sentence)
            else:
                cursor.execute(sql_sentence)

    def get_UID(self, cursor):
        if hasattr(cursor, 'lastrowid'):
            return cursor.lastrowid
        return None

    @abstractmethod
    def is_duplicate_key_error(self, error_msg):
        # type: (str) -> bool
        pass

    @abstractmethod
    def is_foreign_key_error(self, error_msg):
        # type: (str) -> bool
        pass

if __name__ == "__main__":

    from BaseModel import BaseModel

    class MainTableModel(BaseModel):
        def __init__(self):
            BaseModel.__init__(self)
            self.pk_id = None # type: int
            self.anytext = None # type: str

        def is_UID_pk(self):
            return True

        def get_pk_fields(self):
            None

    class DAODelegateTest(DAODelegate):
        def __init__(self, addDef):
            DAODelegate.__init__(self, addDef)

    model = MainTableModel()
    model.anytext = 'Test'

    t = DAODelegateTest(addDef = None)
    t.setAddDefinition("select * from tb_table",True,['anytext'])
    t.executeAddSQL("tt",model)

    print (t)
