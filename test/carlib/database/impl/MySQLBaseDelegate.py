from abc import ABCMeta

from carlib.database.DatabaseDelegate import DatabaseDelegate


class MySQLBaseDelegate(DatabaseDelegate):
    """Delegate default para MySQL Server.

        Implementa lo basico conocido previamente para el comportamiento de los
        drivers soportados , en este caso mysql (mysql.connector).

    """

    __metaclass__ = ABCMeta

    def __init__(self):
        DatabaseDelegate.__init__(self)

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
        if error_msg.find("(23000): Duplicate entry") >= 0:
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
        if (error_msg.find("conflicted with the FOREIGN KEY constraint") >= 0
                or error_msg.find("a foreign key constraint fails") >= 0):
            return True
        return False

    def get_uid(self, handler):
        """
        Retorna el las uid.

        Para el caso de un insert simple via execute esto sera suficiente, para otros casos debera
        hacerse override de esta implementacion,

        Por ejemplo si el insert esta en  un stored procedure y obviamente el ultimo insert es a la tabla
        de interes la implementacion deberia ser :

                handler.execute("SELECT last_insert_id();")
                lastrowid = cursor.fetchone()[0]
                return lastrowid

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia,
            en este caso seria el cursor.

        Returns
        -------
        int
            El unique id o None de no existir, por default devuelve el valor que el driver proporciona.

        """
        return handler.lastrowid


