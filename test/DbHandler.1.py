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

            if host is None or port is None or dbname is None or passwd is None or database is None:
                raise ValueError('host,port,dbname,user and passwd parameters are required')

            # Ensamblando el string
            self.conn = self.db.connect(host=host, port=port, database=dbname, user=user, password=passwd)
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
                for i in xrange(len(cur.description)):
                    print("FieldName: %-50s Value: %-50s" % (cur.description[i].name, row[i]))

                print("=================\n")
        finally:
            cur.close()

if __name__ == "__main__":
    dbh = DbHandler()
    dbh.db_connect("192.168.0.5", 5432, "db_atletismo", "postgres", "melivane")

    import mem_profile
    import time

    memb = mem_profile.memory_usage_psutil()
    print ('Memory (Before): {}Mb'.format(memb))

    t1 = time.clock()


    dbh.fetch_atletas()

    t2 = time.clock()

    memf = mem_profile.memory_usage_psutil()
    print ('Memory (After) : {}Mb'.format(memf))
    print ('Diff {} mem'.format(memf-memb))
    print ('Diff {} mem'.format(1024*(memf-memb)))
    print ('Took {} Seconds'.format(t2-t1))

    dbh.db_close()

    supported_drivers = ('pgsql','sqlite3','mysql')
    ff = [driver for driver in supported_drivers if 'sqlite3' in driver]
    print(ff)