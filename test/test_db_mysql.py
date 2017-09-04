def direct_call_id(cur):
    ### MSSQL SERVER ODBC METODO - CON EXECUTE DIRECTO
    cur.execute("SELECT last_insert_id();")
    lastrowid = cur.fetchone()[0]
    #print("lastrowid = {}".format(lastrowid))
    return lastrowid

from DbDriverFactory import DbDriverFactory
#import pymssql

fid = 2294
fname=2294

#type = "directcall"
#type = "directsp"
#type = "call_with_select_id"
#type = "call_with_return_id"
type = "call_with_output_param_id"

result = None

xx = DbDriverFactory.get_db_driver('mysql')

conn = xx.connect(host='localhost', user='root',password='melivane', database='test')
cur = conn.cursor()
try:
    if type == "directcall":
        cur.execute("insert into tb_maintable(anytext) values ('{}')".format(fname))
    elif type == "directsp":
        cur.callproc("addToMaintableWithoutReturn", [fname])
    elif type == "call_with_select_id":
        cur.callproc("addToMainTableWithSelectReturn",[fname])
        #cur.execute("call addToMainTableWithSelectReturn('{}');".format(fname))
    elif type == "call_with_return_id":
        cur.execute("select addToMainTableWithReturn('{}')".format(fname))
    elif type == "call_with_output_param_id":
        cur.callproc("addToMainTableWithOutParam",[fid,0])
        #results = cur.execute("call addToMainTableWithOutParam('{}',@newid);select @newid;".format(fname),multi=True)
    #if cur.rowcount >= 0:
    if type == "directcall":
        # Es independiente del trigger
        lastrowid = cur.lastrowid
        print(lastrowid)
    elif type == "directsp":
        # El stored procedure debe hacer solo insert a la tabla que se requeire el id o el insert debe ser
        # el ultimo dentro del sp, es irrelevante si tiene selects o no ya que seran ignorados.
        # IMPORTANTE : Si se hace mas de un insert en la misma tabla el id sera del ultimo insert
        #   esto es absolutamente raro en produccion , pero valga la advertencia.
        # En el caso se agrege a otras tablas debera usarse otro type mas adecuado, la idea aqui es que solo se agregue
        # a la tabla de interes en el sp.
        #
        print(direct_call_id(cur))
    elif type == "call_with_select_id":
        # El select que contiene el id debera ser el ultimo existente en el stored procedure de lo contrario
        # fallara, si no fuera asi y no se tiene acceso al sp puede crearse uno que envuelva
        # al primero y efectue los select en dicho orden, asi mismo el insert a la tabla que deseamos el last id
        # debera ser la ultima en ser insertada.
        # No se ve afectada por triggers.
        # Solo puede accesarse usando stored_results el cual es una extension pymysql de otra manera no funciona
        # correctamente.
        for result in cur.stored_results():
            lastrowid = result.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_return_id":
        # Es irrelevante si existen selects antes que el return , siempre se recogera
        # como id el ultimo resultado.
        # Esto solo puede ser realizado por una funcion no un sp en mysql, ya que los sp no
        # soportan retornar un valor.
        # No se ve afectada por triggers.
        lastrowid = cur.fetchone()[0]
        while cur.nextset():
            lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_output_param_id":
        # En la interfase python de mysql no existe una manera standard de recoger los output params
        # pero la documentacion indica que los parametros pueden ser accesados como "@_spname_argn"
        # por ende se requiere un select para recoger el valor deseado.
        #
        cur.execute("select @_addToMainTableWithOutParam_arg2")
        print(cur.fetchone()[0])

    conn.commit()
except Exception as ex:
    print(str(ex))
    conn.rollback()
finally:
    cur.close()
    conn.close()
