import sys

class DbHandler:
    def __init__(self, dbType='pgsql'):
        """Initialize the thread."""
        self.conn = None
        self.db = None
        try:
            if dbType == 'pgsql':
                import psycopg2
                self.db = psycopg2

        except:
            raise ImportError('No PostgreSQL library, install psycopg2!')

    def db_connect(self, host, port, dbname, user, passwd):
        # type: (str, int, str, str, str) -> None

        dbinfo = None
        try:
            self.conn = None

            if host is None or port is None or dbname is None or passwd is None:
                raise Exception('Parametros de base de datos incompletos!')

            # Ensamblando el string
            dsn = "host=%s port=%s dbname=%s user=%s password=%s" % (host, port, dbname, user, passwd)
            print(dsn)
            dbinfo = 'db: %s:%s' % (host, dbname)

            self.conn = self.db.connect(dsn)
            print(self.conn)
        except:
            ex = sys.exc_info()
            s = 'Exception: %s: %s\n%s' % (ex[0], ex[1], dbinfo)
            print(s)
            return None

    def db_close(self):
        if self.conn is not None:
            print('Cerrando Coneccion')
            self.conn.close()

    def fetch_atletas(self):
        cur = self.conn.cursor()
        try:
            cur.execute("""SELECT * from tb_atletas""")
            for row in cur.fetchall():
                print("Record\n")
                for i in range(len(cur.description)):
                    print("FieldName: %-50s Value: %-50s" % (cur.description[i].name, row[i]))

                print("=================\n")
        finally:
            cur.close()

if __name__ == "__main__":
    dbh = DbHandler()
    dbh.db_connect("192.168.0.5", 5432, "db_atletismo", "postgres", "melivane")
    dbh.fetch_atletas()
    dbh.db_close()
