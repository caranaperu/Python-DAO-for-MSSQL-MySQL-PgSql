class DatabaseDriverFactory(object):
    """
    Clase factory para obtener una instancia de un driver de base de datos.

    Attributes
    __suported_drivers: tuple of (str)
        Atributo privado el cual contiene la lista de los drivers soportados, actualmente
        se soporta para postgres, mysql, msssql (odbc y pyhon)

    """

    __supported_drivers = ('pgsql', 'mysql', 'mssql', 'mssqlpypy', 'mssqlpy')

    @staticmethod
    def get_db_driver(driver_id):
        """
        Carga el driver identificado por su identificador.

        Este metodo es estatico.

        Parameters
        driver_id: str
            El identificador del driver a cargar el cual debe ser uno de los siguientes:
                pgsql       - para postgres y cargara el driver psycopg2.
                mysql       - para MySQL cargara el driver mysql.connector
                mssql       - para Microsoft SQL Server ,cargara el driver pymssql
                mssqlpy     - para Microsoft SQL Server ,cargara el driver pyodbc
                mssqlpypy   - para Microsoft SQL Server ,cargara el driver pypyodbc

        Returns
        object
            Instancia de driver de base de datos.

        Raises
        ValueError
            Si el parametro driver_id no identifica a uno soportado.

        """
        driver = [drv for drv in DatabaseDriverFactory.__supported_drivers if driver_id in drv]

        if not driver:
            raise ValueError('db driver {} not supported'.format(driver_id))
        else:
            if driver[0] == 'pgsql':
                import psycopg2
                return psycopg2
            elif driver[0] == 'mysql':
                import mysql.connector
                return mysql.connector
            elif driver[0] == 'mssql':
                import pymssql
                return pymssql
            elif driver[0] == 'mssqlpypy':
                import pypyodbc
                return pypyodbc
            elif driver[0] == 'mssqlpy':
                import pyodbc
                return pyodbc
        return None

    @staticmethod
    def driver_is_odbc(driver_id):
        """
        Indica si un driver esta basado en ODBC.

        Este metodo es estatico.

        Parameters
        driver_id: str
            El identificador del driver a cargar el cual debe ser uno de los siguientes:
                pgsql       - para postgres y cargara el driver psycopg2.
                mysql       - para MySQL cargara el driver mysql.connector
                mssql       - para Microsoft SQL Server ,cargara el driver pymssql
                mssqlpy     - para Microsoft SQL Server ,cargara el driver pyodbc
                mssqlpypy   - para Microsoft SQL Server ,cargara el driver pypyodbc

        Returns
        bool
            true si es un driver basado en ODBC.

        Raises
        ValueError
            Si el parametro driver_id no identifica a uno soportado.

        """
        driver = [drv for drv in DatabaseDriverFactory.__supported_drivers if driver_id in drv]

        if not driver:
            raise ValueError('db driver {} not supported'.format(driver_id))

        if driver_id == 'mssqlpypy' or driver_id == 'mssqlpy':
            return True
        return False

    @staticmethod
    def driver_encoding(driver_id):
        """
        En el caso que el driver este soportado en ODBC retorna el encoding default del driver.

        Se requiere ya que se ha notado que por default no usan UTF-8.
        Este metodo es estatico.

        Parameters
        driver_id: str
            El identificador del driver a cargar el cual debe ser uno de los siguientes:
                pgsql       - para postgres y cargara el driver psycopg2.
                mysql       - para MySQL cargara el driver mysql.connector
                mssql       - para Microsoft SQL Server ,cargara el driver pymssql
                mssqlpy     - para Microsoft SQL Server ,cargara el driver pyodbc
                mssqlpypy   - para Microsoft SQL Server ,cargara el driver pypyodbc

        Returns
        str
            con el encoding si es un driver ODBC o None de no serlo.

        Raises
        ValueError
            Si el parametro driver_id no identifica a uno soportado, en este caso la excepcion
            sera enviado en el metodo de deteccion si el driver es ODBC.

        """
        if DatabaseDriverFactory.driver_is_odbc(driver_id):
            return DatabaseDriverFactory.get_db_driver(driver_id).odbc_encoding
        return None
