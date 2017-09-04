def direct_call_id(cur):
    ### MSSQL SERVER ODBC METODO - CON EXECUTE DIRECTO
    cur.execute("select SCOPE_IDENTITY();")
    lastrowid = cur.fetchone()[0]
    print("lastrowid = {}".format(lastrowid))
    return lastrowid

from DbDriverFactory import DbDriverFactory
#import pymssql

fid = 2297
fname=2297

#type = "directcall"
#type = "directsp"
#type = "call_with_select_id"
#type = "call_with_return_id"
type = "call_with_output_param_id"

result = None

xx = DbDriverFactory.get_db_driver('mssqlpypy')

cstr = 'DSN=MSSQLServer;SERVER=192.168.0.9;DATABASE=pytest;UID=sa;PWD=melivane;'
#conn = xx.connect(host='192.168.0.9', user='sa',password='melivane', database='pytest')
#conn = xx.connect(driver='MSSQLServer',server='192.168.0.9',database='pytest',uid='sa',pwd='melivane')
conn = xx.connect(cstr)
cur = conn.cursor()
try:
    if type == "directcall":
        cur.execute("insert into tb_factura4(factura_id,factura_fecha,name,tb_factura_item_id) values ({},'{}','{}',{})".format(fid,'2017-01-01',fname,2))
    elif type == "directsp":
        raise Exception('No soportado..')
    elif type == "call_with_select_id":
        cur.execute("set nocount on;EXEC uspaddFactura4 {},'{}';".format(fid,fname))
    elif type == "call_with_return_id":
        cur.execute("set nocount on;declare @id int;EXEC @id = uspaddFactura5 {},'{}';select @id;".format(fid,fname))
    elif type == "call_with_output_param_id":
        cur.execute("set nocount on;declare @id int;declare @pp varchar(10);EXEC uspaddFactura6 {},'{}',@id output,@pp output;select @pp;select @id;".format(fid,fname))

    if cur.description:
        field_names = [i[0] for i in cur.description]
        print(field_names)
    #if cur.rowcount >= 0:
    if type == "directcall":
        cur.execute("select SCOPE_IDENTITY();")
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
        #print("lastrowid = {}".format(direct_call_id(cur)))
    elif type == "call_with_select_id":
        # El select que contiene el id debera estar antes que cualquier otro select existente en el
        # stored procedure , si no fuera asi y no se tiene acceso al sp puede crearse uno que envuelva
        # al primero y efectue los select en dicho orden.
        # No se ve afectada por triggers ya que el id es recogido programaticamente y seleccionado
        # para ser recogido , por ende el orden posterior al insert es irrelevante.
        # Los sp no pueden tener el set count off !!!!
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_return_id":
        # Es irrelevante si existen selects antes que el return , siempre se recogera
        # como id el ultimo resultado.
        # No se ve afectada por triggers ya que el id es recogido programaticamente y seleccionado
        # para ser recogido , por ende el orden posterior al insert es irrelevante.
        # Los sp no pueden tener el set count off !!!!
        #lastrowid = cur.fetchone()[0]
        lastrowid = cur.fetchone()[0]
        while cur.nextset():
            lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_output_param_id":
        # EL controlador pyodbc o pypyodbc no soportan output parameters , por ende se tiene que simular
        # y el mayor problema es que si el stored procedure a la vez retorna algun select al menos
        # estos resultados vendran primero y al final el output parameter sera recogido , por ende
        # se recorreran todos los resultados y el ultimo encontrado sera el id.
        # Para que esto funcione el stored procedure sera modificado antes de ejecutarse a la siguiente
        # manera:
        #   set nocount on;declare @out_param int;EXEC my_sp_with_out_params param1,param2,param...,@out_param output;select @out_param
        # En el caso que existan mas de un output parameter , EL ULTIMO EN SER RECOGIDO debe ser el UNIQUE ID.
        #
        # Los sp no pueden tener el set count off !!!!
        #
        lastrowid = cur.fetchone()[0]
        while cur.nextset():
            lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))

    conn.commit()
except Exception as ex:
    print(str(ex))
    conn.rollback()
finally:
    cur.close()
    conn.close()
