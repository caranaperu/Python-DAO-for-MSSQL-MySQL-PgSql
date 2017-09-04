from typing import Dict, Any
from DbDriverFactory import DbDriverFactory

class TransactionException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class TransactionManager(object):

    def __init__(self, db_driver_id, db_params):
        # type: (str, Dict[str,Any]) -> None
        """Initialize  variables."""
        self.__db_driver_id = db_driver_id  # type: str
        self.__db_params = db_params  # type: Dict[str,Any]
        self.__connection = None  # type: object
        self.__cursor = None  # type: object
        self.__trxcount = 0  # type: int
        self.__db_driver = DbDriverFactory.get_db_driver(self.__db_driver_id)



    def start_transaction(self):
        if (self.__trxcount == 0):
            # initialize the db driver
            try:
                self.__connection = self.__db_driver.connect(
                    host=self.__db_params['host'], port=self.__db_params['port'],
                    database=self.__db_params['database'], user=self.__db_params['user'],
                    password=self.__db_params['password'])
            except Exception as ex:
                print(ex)
                raise TransactionException("Cant load driver with parameters {host},{port},{database},{user},{password}".format(**self.__db_params))
        self.__trxcount += 1

    def end_transaction(self, has_error=False):
        if (self.__connection is None or self.__trxcount == 0):
            return

        if (has_error):
            self.__connection.rollback()
            self.__trxcount = 0
        elif (self.__trxcount == 1):
            self.__connection.commit()
            self.__trxcount = 0
        else:
            self.__trxcount -= 1

        if (self.__trxcount == 0):
            if (self.__cursor is not None):
                self.__cursor.close()
            self.__connection.close()
            self.__connection = None
            self.__cursor = None

    def get_transaction_cursor(self):
        if (self.__cursor is None):
            if (self.__connection is not None):
                self.__cursor = self.__connection.cursor()
                return self.__cursor
            else:
                raise TransactionException('Transaction not started')
        else:
            return self.__cursor

    @property
    def db_driver(self):
        # type: () -> object
        return self.__db_driver
