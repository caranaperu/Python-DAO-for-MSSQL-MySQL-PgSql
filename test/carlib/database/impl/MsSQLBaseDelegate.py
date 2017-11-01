from abc import ABCMeta

from carlib.database.DatabaseDelegate import DatabaseDelegate


class MsSQLBaseDelegate(DatabaseDelegate):
    """Delegate default para Micrososft Sql Server

        Implementa lo basico conocido previamente para el comportamiento de los
        drivers soportados , en este caso mssql (pymssql), mssqlpy (pyodbc) ,
        mssqlpypy (pypyodbc).

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        DatabaseDelegate.__init__(self)

        # Por default si no se define por el que requiere este delegate
        # sera para mssql que carga el driver pymssql
        self.driver_id = 'mssql'

    def is_duplicate_key_error(self, error_msg):
        """
        implementacion especifica para pgsql (psycopg2).

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usado para indicar si es un error de llave duplicada o no.

        Returns
        -------
        bool
            True si es un error de llave duplicada , False de lo contrario.

        """
        if error_msg.find("DB-Lib error message 2627, severity 14") >= 0 or \
                        error_msg.find("DB-Lib error message 2601, severity 14") >= 0 or \
                        error_msg.find('Violation of UNIQUE KEY constraint') >= 0 or \
                        error_msg.find('Cannot insert duplicate key row') >= 0:
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        """
        implementacion especifica para mysql (mysql.connector) soportada.

        Parameters
        ----------
        error_msg: str
            Con el mensaje retornado por la persistencia a traves de una exception, el cual sera
            usado para indicar si es un error de foreign key o no.

        Returns
        -------
        bool
            True si es un error de foreign key , False de lo contrario.

        """
        # El primer chequeo es para odbc drivers , el otro es para pymssql
        if ((error_msg.find("DB-Lib error message 547, severity 16") >= 0
             and error_msg.find("FOREIGN KEY constraint") >= 0)
            or error_msg.find("conflicted with the FOREIGN KEY constraint") >= 0
            or error_msg.find("statement conflicted with the REFERENCE constraint") >= 0):
            return True
        return False

    def get_uid(self, handler):
        """
        Retorna el last uid.

        Dado que el soporte es via odbc (pypyodbc,pyodbc) y via pymssql , el soporte depende del caso
        para el caso no ODBC lastrowid es suficiente pero para los casos ODBC sera necesario llamar a
        SCOPE_IDENTITY.

        Por ejemplo si el insert esta en  un stored procedure y obviamente el ultimo insert es a la tabla
        de interes la implementacion deberia ser :

                handler.execute("SELECT last_insert_id();")
                lastrowid = cursor.fetchone()[0]
                return lastrowid

        Este mismo seria usado via ODBC para inserts simples pero en el caso no ODBC lastrowid sera suficiente.

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia,
            en este caso seria el cursor.

        Returns
        -------
        int
            El unique id o None de no existir, por default devuelve el valor que el driver proporciona para el caso
            no ODBC , para el caso ODBC se llamara a SCOPE_IDENTITY

        """
        if hasattr(handler, 'lastrowid'):
            return handler.lastrowid
        else:
            handler.execute("select SCOPE_IDENTITY();")
            lastrowid = handler.fetchone()[0]
            return lastrowid
