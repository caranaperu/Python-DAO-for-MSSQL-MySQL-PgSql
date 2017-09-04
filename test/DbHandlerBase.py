import sys

class DbHandlerBase(object):
    def __init__(self, dbType="pgsql"):
        # type: (str) -> None
        """Initialize the db driver."""
        self.__conn = None
        self.__db_driver = None
        try:
            if dbType == 'pgsql':
                import psycopg2
                self.__db_driver = psycopg2
            else:
                raise ValueError('Debe indicar un driver soportado [pgsql]')
        except ImportError:
            raise ImportError('No Database Library, install requiered libraries for %s ' % dbType)

    def db_connect(self, host, port, dbname, user, passwd):
        # type: (str, int, str, str, str) -> None

        dbinfo = None
        try:
            self.__conn = None

            if host is None or port is None or dbname is None or passwd is None:
                raise ValueError('Parametros de base de datos incompletos defina host,port,dbname.user,password!')

            # Ensamblando el string
            dsn = "host=%s port=%s dbname=%s user=%s password=%s" % (host, port, dbname, user, passwd)
            print(dsn)
            dbinfo = 'db: %s:%s' % (host, dbname)

            self.__conn = self.__db_driver.connect(dsn)
            print(self.__conn)
        except:
            ex = sys.exc_info()
            print('Exception: %s: %s\n%s' % (ex[0], ex[1], dbinfo))
            return None

    def db_close(self):
        if self.__conn is not None:
            print('Cerrando Coneccion')
            self.__conn.close()

    def fetch_atletas(self):
        cur = self.__conn.cursor()
        try:
            cur.execute("""SELECT * from tb_atletas""")
            for row in cur.fetchall():
                print("Record\n")
                for i in range(len(cur.description)):
                    print("FieldName: %-50s Value: %-50s" % (cur.description[i].name, row[i]))

                print("=================\n")
        finally:
            cur.close()


