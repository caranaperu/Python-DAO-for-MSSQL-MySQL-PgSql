def direct_call_id(cur):
    ### MSSQL SERVER ODBC METODO - CON EXECUTE DIRECTO
    cur.execute("select SCOPE_IDENTITY();")
    lastrowid = cur.fetchone()[0]
    print("lastrowid = {}".format(lastrowid))
    return lastrowid

from DbDriverFactory import DbDriverFactory

fid = 2297
fname=2297

#type = "directcall"
type = "directsp"
#type = "call_with_select_id"
#type = "call_with_return_id"
#type = "call_with_output_param_id"

result = None

xx = DbDriverFactory.get_db_driver('pgsql')

conn = xx.connect(host='192.168.0.5', user='postgres',
                  password='melivane', database='db_pytest')
cur = conn.cursor()
try:
    if type == "directcall":
        cur.execute("insert into tb_maintable(id_key,anytext) values (DEFAULT,'{}') returning id_key".format(fname))
    elif type == "directsp":
        cur.execute("select directspInsertTest('{}');".format(fname))

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
        # La mejor manera que existe en postgres es usar la clausula returning con el id
        # es infailble bajo cualquier situacion y mas confiable en multiuser.
        # Importante si se desea usar POSTGRES-XC es necesario usar currval.
        #           Asi mismo para postgres < 8.2 esa seria la solucion ya que no existe el returning.
        # hay que agregar que lastrowid del cursor no retorna un valor correcto los autores de psycopg2
        # no lo recomiendan.
        # El metodo returning es infalibe en el extrano caso que un trigger insertara otro registro
        # a la misma tabla (caso muy remoto).
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "directsp":
        # Se supone que en este sp se agregara el registro a la tabla y se espera un solo insert
        # a la misma , de no ser asi usar otro de los metodos aceptados como :
        #   call_with_select_id , call_with_return_id o call_with_output_param_id
        #
        # Asi mismo no funcionara si en un trigger que se dispare por un after insert agrega
        # otro registro a la misma tabla , ya que el id retornado sera el del ultimo agregado.
        #
        # Dado que CURRVAL dara el ultimo id agregado a esa tabla si se cumplen las condiciones
        # indicadas arriba , el resultado sera el correcto.
        cur.execute("SELECT CURRVAL(pg_get_serial_sequence('tb_maintable','id_key'))")
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
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
