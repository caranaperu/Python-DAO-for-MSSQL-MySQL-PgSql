from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

def direct_call_id(cur):
    cur.execute("SELECT last_insert_id();")
    lastrowid = cur.fetchone()[0]
    return lastrowid

from DbDriverFactory import DbDriverFactory
#import pymssql

fname='Test'

#type = "directcall"
#type = "directsp"
#type = "call_with_select_id"
#type = "call_with_return_id"
type = "call_with_output_param_id"

result = None

xx = DbDriverFactory.get_db_driver('mysql')

conn = xx.connect(host='localhost', user='root',password='melivane', database='py_dbtest')
cur = conn.cursor()
try:
    if type == "directcall":
        cur.execute("insert into tb_maintable(anytext) values ('{}')".format(fname))
    elif type == "directsp":
        cur.callproc("directspInsertTest", [fname])
    elif type == "call_with_select_id":
        cur.callproc("withSelectspInsertTest",[fname])
        #cur.execute("call addToMainTableWithSelectReturn('{}');".format(fname))
    elif type == "call_with_return_id":
        cur.execute("select withReturnspInsertTest('{}')".format(fname))
    elif type == "call_with_output_param_id":
        cur.callproc("withOutParamInsertTest",[fname,0])
        #results = cur.execute("call addToMainTableWithOutParam('{}',@newid);select @newid;".format(fname),multi=True)
    #if cur.rowcount >= 0:
    if type == "directcall":
        # Es independiente del trigger, mas aun cuando aqui el trigger no puede insertar a la misma
        # tabla (Limitacion MySQL) , Para pruebas crear un trigger con un id autoincrement en otra
        # tabla.
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
        # El last insert id no toma en cuenta lo que suceda dentro de un trigger.
        #
        # En este caso lastrowid del cursor no retorna un valor valido.
        cur.execute("SELECT last_insert_id();")
        lastrowid = cur.fetchone()[0]
        print(lastrowid)
    elif type == "call_with_select_id":
        # El select que contiene el id debera ser el ultimo existente en el stored procedure de lo contrario
        # fallara, si no fuera asi y no se tiene acceso al sp puede crearse uno que envuelva
        # al primero y efectue los select en dicho orden, asi mismo el insert a la tabla que deseamos el last id
        # debera ser la ultima en ser insertada.
        # No se ve afectada por triggers.
        # Solo puede accesarse usando stored_results el cual es una extension pymysql de otra manera no funciona
        # correctamente. (Esto para el caso que existen otros selects previos al ultimo)
        for result in cur.stored_results():
            lastrowid = result.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_return_id":
        # En mysql para retornar un valor via return y no select , solo es valido via una funcion,
        # asi mismo estas no soportan resultados de resultset , por ende aqui el resultado directo
        # es todo lo que se necesita.
        # No se ve afectada por triggers.
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_output_param_id":
        # En la interfase python de mysql no existe una manera standard de recoger los output params
        # pero la documentacion indica que los parametros pueden ser accesados como "@_spname_argn"
        # por ende se requiere un select para recoger el valor deseado y conocer su posicion en el
        # call.
        #
        cur.execute("select @_withOutParamInsertTest_arg2")
        print(cur.fetchone()[0])

    conn.commit()
except Exception as ex:
    print(str(ex))
    conn.rollback()
finally:
    cur.close()
    conn.close()
