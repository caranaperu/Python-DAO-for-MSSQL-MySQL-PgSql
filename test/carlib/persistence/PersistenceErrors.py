from enum import IntEnum


class PersistenceErrors(IntEnum):
    """Enumeracion con los errores que retornara a la implementacion de PersistenceOperations."""

    DB_OP_OK = 0
    DB_ERR_ALLOK = 100000
    DB_ERR_SERVERNOTFOUND = 100001
    DB_ERR_RECORDNOTFOUND = 100002
    DB_ERR_RECORDNOTDELETED = 100003
    DB_ERR_RECORDEXIST = 100004
    DB_ERR_FOREIGNKEY = 100005
    DB_ERR_CANTEXECUTE = 100006
    DB_ERR_RECORD_MODIFIED = 100007
    DB_ERR_RECORDINACTIVE = 100008
    DB_ERR_DUPLICATEKEY = 100009
    DB_ERR_TOOMANYRESULTS = 100010
