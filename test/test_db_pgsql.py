def direct_call_id(cur):
    ### MSSQL SERVER ODBC METODO - CON EXECUTE DIRECTO
    cur.execute("select SCOPE_IDENTITY();")
    lastrowid = cur.fetchone()[0]
    print("lastrowid = {}".format(lastrowid))
    return lastrowid

from DatabaseDriverFactory import DatabaseDriverFactory

fname=2297

#type = "directcall"
#type = "directsp"
#type = "call_with_select_id"
#type = "call_with_return_id"
type = "call_with_output_param_id"

result = None

xx = DatabaseDriverFactory.get_db_driver('pgsql')

conn = xx.connect(host='192.168.0.5', user='postgres',
                  password='melivane', database='db_pytest')
cur = conn.cursor()
try:
    if type == "directcall":
        cur.execute("insert into tb_maintable(id_key,anytext) values (DEFAULT,'{}') returning id_key".format(fname))
    elif type == "directsp":
        cur.execute("select directspInsertTest('{}');".format(fname))
    elif type == "call_with_select_id":
        cur.execute("select withSelectspInsertTest('{}');".format(fname))
    elif type == "call_with_return_id":
        cur.execute("select withReturnspInsertTest('{}');".format(fname))
    elif type == "call_with_output_param_id":
        cur.execute("select * from withOutParamInsertTest('{}');".format(fname))
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
        # CURRVAL dara el ultimo id agregado a esa tabla independientemente de cual sea el origen
        # del insert el sp o un trigger after insert.
        cur.execute("SELECT CURRVAL(pg_get_serial_sequence('tb_maintable','id_key'))")
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_select_id":
        # En este caso no se ve afectada por triggers ya que el id es recogido programaticamente
        # y seleccionado para ser recogido , por ende el orden posteriorde otras sentencias al insert
        # es irrelevante.
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_return_id":
        # En este caso no se ve afectada por triggers ya que el id es recogido programaticamente
        # y seleccionado para ser recogido , por ende el orden posterior al insert es irrelevante.
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    elif type == "call_with_output_param_id":
        # En este caso los output parameters son retornados como un solo registro en el orden declarado
        # se requerira saber cual es el que representa el idenity.
        # Dado que es programatico es irrelevante si hay trigger o selects previos , etc.
        #
        lastrowid = cur.fetchone()[0]
        print("lastrowid = {}".format(lastrowid))
    conn.commit()
except Exception as ex:
    print(str(ex))
    conn.rollback()
finally:
    cur.close()
    conn.close()
