class DbDriverFactory(object):

    __supported_drivers = ('pgsql', 'sqlite3', 'mysql', 'mssql', 'mssqlpypy', 'mssqlpy')

    @staticmethod
    def get_db_driver(driver_id):
        # type: (str) -> object

        driver = [drv for drv in DbDriverFactory.__supported_drivers if driver_id in drv]

        if (not driver):
            raise ValueError('db driver {} not supported'.format(driver_id))
        else:
            if (driver[0] == 'pgsql'):
                import psycopg2
                return psycopg2
            elif (driver[0] == 'sqlite3'):
                import sqlite3
                return sqlite3
            elif (driver[0] == 'mysql'):
                import mysql.connector
                return mysql.connector
            elif (driver[0] == 'mssql'):
                import pymssql
                return pymssql
            elif (driver[0] == 'mssqlpypy'):
                import pypyodbc
                return pypyodbc
            elif (driver[0] == 'mssqlpy'):
                import pyodbc
                return pyodbc
        return None
