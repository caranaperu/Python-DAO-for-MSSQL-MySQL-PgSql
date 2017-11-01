from abc import ABCMeta

from carlib.database.DatabaseDelegate import DatabaseDelegate


class PgSQLBaseDelegate(DatabaseDelegate):
    """Delegate default para PostgreSql Server.

        Implementa lo basico conocido previamente para el comportamiento de los
        drivers soportados , en este caso pgsql (psycopg2).

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
        if error_msg.find("duplicate key value violates unique constraint") >= 0:
            return True
        return False

    def is_foreign_key_error(self, error_msg):
        """
        implementacion especifica para pgsql (psycopg2) soportada.

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
        if error_msg.find("violates foreign key constraint") >= 0:
            return True
        return False

    def get_uid(self, handler):
        """
        Se recomienda usar la clausula INSERT....RETURNING la cual garantiza adquirir el last id
        insertado sin limitaciones ni necesidad de OIDs.

        Con la clausula returning con el id es infalible bajo cualquier situacion y mas confiable
        en multiuser.
        Importante si se desea usar POSTGRES-XC es necesario usar currval.
                   Asi mismo para postgres < 8.2 esa seria la solucion ya que no existe el returning.

        hay que agregar que lastrowid del cursor no retorna un valor correcto los autores de psycopg2
        no lo recomiendan.

        El metodo returning es infalibe en el extrano caso que un trigger insertara otro registro
        a la misma tabla (caso muy remoto).

        Por ejemplo se recomienda:

        insert into tb_maintable(id_key,anyfield) values (DEFAULT,'afieldvalue') returning id_key

        En cuyo caso para recoger el lastrowid este metodo deberia ser implementado de la siguiemnte manera:

            lastrowid = cursor.fetchone()[0]
            return lastrowid

        En el caso que se ejecute un stored procedure y querramos recoger el ultimo insert a una tabla este
        seria implementado como :

            cursor.execute("SELECT CURRVAL(pg_get_serial_sequence('th_table_name','the_unique_id_field'))")
            lastrowid = cursor.fetchone()[0]
            return lastrowid

        Parameters
        ----------
        handler: object
            Representa el objeto a traves del cual se ejecutara la operacion en la persistencia.
            Si la persistencia es una base de datos , este seria por ejemplo el cursor.

        Returns
        -------
        int
            El unique id o None de no existir, por default devuelve el valor que el driver proporciona.

        """
        return handler.lastrowid


