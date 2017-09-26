from collections import defaultdict
from DatabaseDriverFactory import DatabaseDriverFactory


class TransactionManagerException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TransactionManager(object):
    """
    Controla la transaccion que pueda ser usada por multiples instancias de DatabasePersistence clases.

    Si es usado por multiples instancias de DatabasePersistence mantendra la transaccion viva entre ambas
    para lo cual el transacion manager debera ser externo a ambas.

    Si es usado dentro de un mismo DatabasePersistence entre operaciones , este hara el commit al final de
    la ultima operacion.

    Examples
    --------
        # Es pseudo code
        trx = TransactionManager('mssql', {'host': '192.168.0.9', 'port': '1433',
                                   'user': 'sa', 'password': 'melivane', 'database': 'pytest'})
        dao = someDbPersistenceClass(trx,db_delegate)

        trx.start_transaction()

        ret = dao.add(someModel_1)
        if ret == PersistenceErrors.DB_ERR_ALLOK:
            dao.add(someModel_2)

        trx.end_transaction()

    """

    def __init__(self, db_driver_id, db_params):
        """
        Initialize  variables.

        Parameters
        ----------
        db_driver_id: str
            El identificador del driver a cargar el cual debe ser uno de los siguientes:
                pgsql       - para postgres y cargara el driver psycopg2.
                mysql       - para MySQL cargara el driver mysql.connector
                mssql       - para Microsoft SQL Server ,cargara el driver pymssql
                mssqlpy     - para Microsoft SQL Server ,cargara el driver pyodbc
                mssqlpypy   - para Microsoft SQL Server ,cargara el driver pypyodbc
        db_params: dict[str,str]
            Diccionario conteniendo los parametros de inicializacion del driver de base de datos.
                dsn
                host
                port
                database
                user
                password
            dsn es usado por los drivers basados en ODBC , los demas son utilizados en otrs drivers y ODBC
            segun sea el caso , verificar la documentacion del driver elegido para usar.

        """
        self.__db_driver_id = db_driver_id
        self.__db_params = db_params
        self.__connection = None
        self.__cursor = None
        self.__trxcount = 0
        self.__db_driver = DatabaseDriverFactory.get_db_driver(self.__db_driver_id)

    def start_transaction(self):
        """
        Inicia la transaccion y carga el driver si es la primera operacion.

        Mantiene un contador para determinar el numero de operaciones bajo la instancia del
        transaction manager , esto permitira que se haga el commit cuando este llegue a 0.

        Returns
        -------
        None

        Raises
        ------
        TransactionManagerException
            Si no ha sido inicializar el driver solicitado.

        """
        if self.__trxcount == 0:
            # initialize the db driver
            try:
                if DatabaseDriverFactory.driver_is_odbc(self.__db_driver_id):
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
                raise TransactionManagerException(
                    "Cant load driver with parameters dsn={0[dsn]},host={0[host]},port={0[port]},database={0[database]},user={0[user]},password={0[password]}".format(
                        defaultdict(lambda: 'None', self.__db_params)))
        self.__trxcount += 1

    def end_transaction(self, has_error=False):
        """
        Efectua el commit o rollback a la transaccion segun sea el caso..

        Solo hara commit si es que el contador interno indica que es la ultima operacion , hara
        rollback si has_errors es True.

        Parameters
        ----------
        has_error: bool
            Si es True indicara que ha habido algun error durante una operacion bajo esta transaccion,
            por ende se debera efectuar el rollback e impedir que cualquier operacion posterior se
            realize.

        Returns
        -------
        None

        """
        if self.__connection is None or self.__trxcount == 0:
            return

        if has_error:
            self.__connection.rollback()
            self.__trxcount = 0
        elif self.__trxcount == 1:
            self.__connection.commit()
            self.__trxcount = 0
        else:
            self.__trxcount -= 1

        if self.__trxcount == 0:
            if self.__cursor is not None:
                self.__cursor.close()
            self.__connection.close()
            self.__connection = None
            self.__cursor = None

    def get_transaction_cursor(self):
        """
        Devuelve el cursor sobre el cual tiene efecto esta transaccion.

        Returns
        -------
        object
            Con el cursor bajo la transaccion.

        Raises
        ------
        TransactionManagerException
            En el caso que la connection no este aun inicializada , por ende no hay cursor.

        """
        if self.__cursor is None:
            if self.__connection is not None:
                self.__cursor = self.__connection.cursor()
                return self.__cursor
            else:
                raise TransactionManagerException('Transaction not started')
        else:
            return self.__cursor

    def encoding(self):
        """
        Devuelve el encoding sobre el que trabaja el driver usado.

        Este metodo es utilitario para no consultar directamente al driver..

        Returns
        -------
        str
            Con el encoding como por ejemplo UTF-8.

        """
        return DatabaseDriverFactory.driver_encoding(self.__db_driver_id)

    @property
    def db_driver(self):
        """

        Returns
        ------
        object
            Con la instancia del driver cargado por esta instacia de transaction manager.

        """
        return self.__db_driver

    @property
    def db_driver_id(self):
        """

        Returns
        -------
        str
            Con el identificador del driver en uso por el transaction manager..

        """
        return self.__db_driver_id
