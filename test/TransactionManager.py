from typing import Dict, Any
from collections import defaultdict
from DbDriverFactory import DbDriverFactory


class TransactionManagerException(Exception):
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
                if DbDriverFactory.driver_is_odbc(self.__db_driver_id):
                    server_id = self.__db_params['host']
                    if 'port' in self.__db_params:
                        server_id = "{},{}".format(
                            self.__db_params['host'], self.__db_params['port'])

                    self.__connection = self.__db_driver.connect(
                        dsn=self.__db_params['dsn'],
                        server=server_id,
                        database=self.__db_params['database'],
                        uid=self.__db_params['user'],
                        pwd=self.__db_params['password']
                    )
                else:
                    self.__connection = self.__db_driver.connect(
                        host=self.__db_params['host'],
                        port=self.__db_params['port'],
                        database=self.__db_params['database'],
                        user=self.__db_params['user'],
                        password=self.__db_params['password']
                    )
            except Exception as ex:
                print(ex)
                raise TransactionManagerException(
                    "Cant load driver with parameters dsn={0[dsn]},host={0[host]},port={0[port]},database={0[database]},user={0[user]},password={0[password]}".format(defaultdict(lambda: 'None', self.__db_params)))
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
                raise TransactionManagerException('Transaction not started')
        else:
            return self.__cursor

    def encoding(self):
        return DbDriverFactory.driver_encoding(self.__db_driver_id)

    @property
    def db_driver(self):
        # type: () -> object
        return self.__db_driver

    @property
    def db_driver_id(self):
        # type: () -> str
        return self.__db_driver_id


if __name__ == "__main__":

    trx = TransactionManager('mssql', {'dsn': 'MSSQLServer', 'host': '192.168.0.9', 'port': '1433',
                                       'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})
    trx.start_transaction()
    trx.end_transaction()

    trx = TransactionManager('mssqlpy', {'dsn': 'MSSQLServer', 'host': '192.168.0.9', 'port': '1433',
                                         'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})
    trx.start_transaction()
    trx.end_transaction()

    trx = TransactionManager('mssqlpy', {'dsn': 'MSSQLServer', 'host': '192.168.0.9',
                                         'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})
    trx.start_transaction()
    trx.end_transaction()

    trx = TransactionManager('mssqlpypy', {'dsn': 'MSSQLServer', 'host': '192.168.0.9', 'port': '1433',
                                           'user': 'sa', 'password': 'melivane', 'database': 'db_pytest'})
    trx.start_transaction()
    trx.end_transaction()

    trx = TransactionManager('mssqlpypy', {'dsn': 'MSSQLServer', 'host': '192.168.0.9',
                                           'user': 'sa2', 'password': 'melivane', 'database': 'db_pytest'})
    trx.start_transaction()
    trx.end_transaction()
