import re

from carlib.persistence.Constraints import Constraints


def get_filter_operator(driver_id, filter_type):
    """
    Mapea el operador del query a la especifica base de datos.

    Dado que no todos los operadores son tomados exactamente igual en todas las db, este
    metodo permite mapear al especifico si fuera necesario.

    Postgres por ejemplo trata ilike diferente de like otras bases de datos no tienen ese operador
    por ende ilike podria ser mapeado a like.

    Por ejemplo:
        print(get_filter_operator('pgsql', Constraints.FilterType.PARTIAL))  retornara 'like'
        print(get_filter_operator('pgsql', Constraints.FilterType.IPARTIAL)) retornara 'ilike'
        print(get_filter_operator('other', Constraints.FilterType.PARTIAL))  retornara 'like'
        print(get_filter_operator('other', Constraints.FilterType.IPARTIAL)) retornara 'like'

    Parameters
    ----------
    driver_id: str
            El identificador del driver de db api.
            Puede ser:
            pgsql
            mssql
            mssqlpypy
            mssqlpy
            mysql

            Cualquier otro valor no esta soportado y simplemente devolveria
            el mapeo default.
    filter_type: Constraints.FilterType
        Indicara el tipo de filtro a mapeaer

    Returns
    -------
    str
        Con el valor mapeado a la especifica base de datos , por defaul devuelve el valor
        prefijado para el tipo de operador de filtro amenos que IPARTIAL sea requerido en
        cuyo caso retornar el valor de PARTIAL que es el normal en la mayoria de DBs.

    """
    if driver_id == 'pgsql':
        return filter_type.value
    else:
        if filter_type == Constraints.FilterType.IPARTIAL:
            return Constraints.FilterType.PARTIAL.value
        return filter_type.value


def get_as_bool(driver_id, bool_value):
    """
    Dado que no todas las bases de datos tratan el bool igual , aqui podemos mapear.

    Postgres por ejemplo trata los booleanos como 'Y' and 'N' otros simplemente como
    true o false.

    Por ejemplo:
        print(get_as_bool('pgsql', True)) retornara 'Y'
        print(get_as_bool('pgsql', False)) retornara 'N'
        print(get_as_bool('other', True))  retornara true
        print(get_as_bool('other', False)) retornara false

    Parameters
    ----------
    driver_id: str
        El identificador del driver de db api.
        Puede ser:
        pgsql
        mssql
        mssqlpypy
        mssqlpy
        mysql

        Cualquier otro valor no esta soportado y simplemente devolveria
        el mapeo default.
    bool_value: bool
        booleano a mapearse la base de datos.

    Returns
    -------
    str
        Con el valor mapeado a la especifica base de datos , si el parametro no fuera
        booleano sera retornado como false.

    """
    if driver_id == 'pgsql':
        if bool_value is True:
            return 'Y'
        else:
            return 'N'
    else:
        if type(bool_value) == bool and bool_value:
            return 'true'
        else:
            return 'false'


def process_fetch_conditions(driver_id, c_constraints):
    """
    helper que genera las clausulas where y order by basado en los constraints
    enviados.
    Por Ejemplo:
        constraints = Constraints()
        constraints.add_filter_field('issotrx',True,Constraints.FilterType.EQUAL)
        constraints.add_filter_field('c_bpartner_id',1009790,Constraints.FilterType.NO_EQUAL)
        constraints.add_filter_field('c_groupdoc_id',None,Constraints.FilterType.NO_EQUAL)
        constraints.add_filter_field('docaction','cl',Constraints.FilterType.IPARTIAL)

        process_fetch_conditions('pgsql',constraints)

        generara la siguiente salida:
             where c_bpartner_id<>1009790 AND c_groupdoc_id is not null AND docaction ilike '%cl%' AND issotrx='Y'
             order by c_bpartner_id DESC,c_groupdoc_id ASC
    Parameters
    ----------
    driver_id: str
        El identificador del driver de db api.
        Puede ser:
        pgsql
        mssql
        mssqlpypy
        mssqlpy
        mysql

        Cualquier otro valor no esta soportado y simplemente devolveria
        el mapeo default.
    c_constraints: Constraints
        Los constraints a usar para generar el string con las clausula sql.

    Returns
    -------
    str
        con el string conteniendo las clausualas where y order by basados en los
        constraints enviados.

    """
    sql = ""

    if c_constraints:
        filter_fields = c_constraints.filter_fields
        if filter_fields:
            num_fields = len(filter_fields)
            sql += " where "

            for i, (field, operator) in enumerate(c_constraints.filter_fields.items()):
                if num_fields > 1 and i >= 1:
                    sql = sql + " AND "

                value = c_constraints.get_filter_field_value(field)
                if value is None:
                    if operator == Constraints.FilterType.EQUAL:
                        sql = sql + field + " is null"
                    else:
                        sql = sql + field + " is not null"
                elif operator == Constraints.FilterType.PARTIAL or operator == Constraints.FilterType.IPARTIAL:
                    sql = sql + field + " " + get_filter_operator(driver_id, operator) + " '%" + str(value) + "%'"
                elif isinstance(value, str):
                    sql += field + get_filter_operator(driver_id, operator) + "'" + str(value) + "'"
                elif isinstance(value, bool):
                    sql += field + get_filter_operator(driver_id, operator) + "'" + get_as_bool(driver_id, value) + "'"
                else:
                    sql += field + get_filter_operator(driver_id, operator) + str(value)

        sort_fields = c_constraints.sort_fields
        if sort_fields:
            num_sort_fields = len(sort_fields)

            if num_sort_fields > 0:
                sql += " order by "

                for i, (field, direction) in enumerate(c_constraints.sort_fields.items()):
                    if i >= 1:
                        sql = sql + ","
                    sql = sql + field + " " + str(direction)
        return sql


def generate_sql_statement(driver_id, sql_string, c_constraints, remove_unused=False):
    """
    helper que genera la clausula sql por reemplazo de valores.

    Esta funcion espera un string con la clausula correspondiente pero que incluye
    placeholders a ser reemplazados por los valores finales basados en los constraints.

    Los placeholder podran ser:
    $ff_FIELD_NAME
    $ff_FIELD_POSITION

    $f_FIELD_NAME
    $f_FIELD_POSITION

    $oFIELD_POSITION

    $l_l
    $l_o

    Los que inician con $ff_ seran reemplazados por el nombre del campo indicado ya sea por
    nombre o posicion a partir de los filter fields contenidos en los constraints.

    Los que inician con $f_ seran reemplazados por el nombre-operador-valor del campo indicado ya sea por
    nombre o posicion a partir de los filter fields contenidos en los constraints.

    Los que inician con $o seran reemplazados por el nombre del campo y direccion de sort  indicado
    por posicion y seran extraidos de los sort fields contenidos en los constraints.

    $l_l y $l_o corresponden a los campos limit y offset de los constraints y el reemplazo sera por
    el valor de los mismos.

    Por Ejemplo:
        constraints = Constraints()
        constraints.add_filter_field('issotrx',True,Constraints.FilterType.EQUAL)
        constraints.add_filter_field('c_bpartner_id',1009790,Constraints.FilterType.NO_EQUAL)
        constraints.add_filter_field('c_groupdoc_id',None,Constraints.FilterType.NO_EQUAL)
        constraints.add_filter_field('docaction','cl',Constraints.FilterType.IPARTIAL)

        constraints.add_sort_field('c_bpartner_id', Constraints.SortType.DESC)
        constraints.add_sort_field('c_groupdoc_id', Constraints.SortType.ASC)

        constraints.offset = 1000
        constraints.limit = 5000

        sql = "select $ff_isotrx,$ff_c_bpartner_id where $f_c_groupdoc_id and $f_docaction
                order by $o0,$o1
                "
        generate_sql_statement('pgsql', sql, constraints)

        retornara lo siguiente:
            select issotrx,c_bpartner_id
                where c_groupdoc_id is null and docaction ilike '%CL%'
            order by c_bpartner_id DESC,c_groupdoc_id ASC
            limit 5000 offset 1000

        Los placeholder posicionales o por nombre pueden intercalarse , de no existir un campo
        en la posicion indicada o no existir un campo con el nombre indicado el placeholder quedara
        intacto.

    Parameters
    ----------
    driver_id: str
        El identificador del driver de db api.
        Puede ser:
        pgsql
        mssql
        mssqlpypy
        mssqlpy
        mysql

        Cualquier otro valor no esta soportado y simplemente devolveria
        el mapeo default.
    sql_string: str
        Conteniendo la clausula con los respectivos placeholders a trabajar.
    c_constraints: Constraints
        Los constraints a usar para generar el string con las clausula sql.
    remove_unused: bool, optional
        Por default es false , si es True y quedan placeholders que no han podido
        ser reemplazados , estos seran retirados. Desde luego que luego de esto no
        se garantiza que el sql de salida este correctamente compuesto.

    Returns
    -------
    str
        con el string conteniendo el sql procesado.

    """
    if c_constraints:
        if c_constraints.filter_fields:
            for i, (field, operator) in enumerate(c_constraints.filter_fields.items()):
                find_patterns = ("$f_" + field, "$f_" + str(i), "$ff_" + field, "$ff_" + str(i), "$fv_" + field)

                field_value = c_constraints.get_filter_field_value(field)
                for j, to_find in enumerate(find_patterns):
                    if j < 2:
                        if (operator == Constraints.FilterType.PARTIAL or
                                    operator == Constraints.FilterType.IPARTIAL):
                            sql_string = sql_string.replace(to_find, field + " " +
                                                            get_filter_operator(driver_id, operator) + " '%" + str(
                                field_value) + "%'")
                        elif isinstance(field_value, str):
                            sql_string = sql_string.replace(to_find, field + " " +
                                                            get_filter_operator(driver_id,
                                                                                operator) + " '" + field_value + "'")
                        elif isinstance(field_value, bool):
                            sql_string = sql_string.replace(to_find, field + " " +
                                                            get_filter_operator(driver_id, operator) + " " + get_as_bool(
                                driver_id, field_value))
                        elif field_value is None:
                            if operator == Constraints.FilterType.EQUAL:
                                sql_string = sql_string.replace(to_find, field + " is null")
                            else:
                                sql_string = sql_string.replace(to_find, field + " is not null")
                        else:
                            sql_string = sql_string.replace(to_find, field + " " +
                                                            get_filter_operator(driver_id, operator) + " " + str(
                                field_value))
                    elif j < 4:
                        sql_string = sql_string.replace(to_find, field)
                    else:
                        sql_string = sql_string.replace(to_find, str(field_value))

        # busqueda de campos para order by
        if c_constraints.sort_fields:
            for i, (field, direction) in enumerate(c_constraints.sort_fields.items()):
                to_find = "$o" + str(i)
                if sql_string.find(to_find) >= 0:
                    sql_string = sql_string.replace(to_find, field + " " + str(direction))
        else:
            if driver_id in ('mssql', 'mssqlpypy', 'mssqlpy') and sql_string.find("FETCH NEXT") >=0:
                sql_string = sql_string.replace("ORDER BY", "ORDER BY(SELECT NULL)")

        # limits
        if c_constraints.limit:
            if sql_string.find("$l_l") >= 0:
                sql_string = sql_string.replace("$l_l", str(c_constraints.limit))
        if c_constraints.offset:
            if sql_string.find("$l_o") >= 0:
                sql_string = sql_string.replace("$l_o", str(c_constraints.offset))

    # Removemos los que no se han usado
    if remove_unused:
        findings = set()
        for m in re.finditer(r"\$ff_[a-zA-Z0-9]+", sql_string):
            findings.add(m.group(0))
        for m in re.finditer(r"\$f_[a-zA-Z0-9]+", sql_string):
            findings.add(m.group(0))
        for m in re.finditer(r"\$fv_[a-zA-Z0-9]+", sql_string):
            findings.add(m.group(0))
        for m in re.finditer(r"\$o[0-9]+", sql_string):
            findings.add(m.group(0))
        for m in re.finditer(r"\$l_[lo]+", sql_string):
            findings.add(m.group(0))

        for finding in findings:
            sql_string = sql_string.replace(","+finding, "")
            sql_string = sql_string.replace(finding, "")
    return sql_string

# if __name__ == "__main__":
#     #######
#     import mem_profile
#     import time
#     import re
#
#     print ('Memory (Before): {}Mb'.format(mem_profile.memory_usage_psutil()))
#
#     daoc = Constraints()
#     daoc.offset = 1000
#     daoc.limit = 5000
#     daoc.add_sort_field('nombres', Constraints.SortType.DESC)
#     daoc.add_sort_field('apellidos', Constraints.SortType.ASC)
#
#     daoc.add_filter_field('codigo', 3, Constraints.FilterType.EQUAL)
#     daoc.add_filter_field(
#         'monto', 100.00, Constraints.FilterType.NO_EQUAL)
#     daoc.add_filter_field('apellidos', "arana reategui",
#                           Constraints.FilterType.EQUAL)
#     daoc.add_filter_field('nombres', "carlos alberto",
#                           Constraints.FilterType.PARTIAL)
#     daoc.add_filter_field(
#         'sueldo', 100.00, Constraints.FilterType.GREAT_THAN)
#     daoc.add_filter_field(
#         'cts', 100.00, Constraints.FilterType.LESS_THAN_EQ)
#     daoc.add_filter_field(
#         'boolfield', "Y", Constraints.FilterType.EQUAL)
#     daoc.add_filter_field('padre', None, Constraints.FilterType.NO_EQUAL)
#     daoc.add_filter_field('madre', None, Constraints.FilterType.EQUAL)
#     print ('Memory (After) : {}Mb'.format(mem_profile.memory_usage_psutil()))
#
#     s = """select * from table t1
#     inner join tb_table2 t2 on t2.$ff_codigo = t1.$ff_codigo
#     where $f_cts and $f_1 and $f_2 or ($f_sueldo and $f_4) and ($f_5 and $f_6 and $f_7 and $f_nombres)
#     and $ff_cts > $fv_cts and $f_boolfield and $fv_xxxx
#     order by $o0,$o1
#     limit $l_l offset $l_o"""

# findings = set()
# for m in re.finditer(r"\$ff_[a-zA-Z0-9]+", s):
#     findings.add(m.group(0))
# print("=====================================")
# for m in re.finditer(r"\$f_[a-zA-Z0-9]+", s):
#     findings.add(m.group(0))
# print("=====================================")
# for m in re.finditer(r"\$fv_[a-zA-Z0-9]+", s):
#     findings.add(m.group(0))
# print("=====================================")
# for m in re.finditer(r"\$o[0-9]+", s):
#     findings.add(m.group(0))
# for m in re.finditer(r"\$l_[lo]+", s):
#     findings.add(m.group(0))
# for st in findings:
#     print(st)
#     #s = s.replace(st,"")

# memb = mem_profile.memory_usage_psutil()
# print ('Memory (Before): {}Mb'.format(memb))
#
# t1 = time.clock()
#
# print(generate_sql_statement('pgsql', s, daoc))
#
# t2 = time.clock()
#
# memf = mem_profile.memory_usage_psutil()
# print ('Memory (After) : {}Mb'.format(memf))
# print ('Diff {} mem'.format(memf - memb))
# print ('Diff {} mem'.format(1024 * (memf - memb)))
# print ('Took {} Seconds'.format(t2 - t1))
#
# import cProfile, StringIO, pstats
#
# pr = cProfile.Profile()
# pr.enable()
# print(generate_sql_statement('pgsql',s, daoc))
# pr.disable()
# s = StringIO.StringIO()
# sortby = 'cumulative'
# ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# ps.print_stats()
# print s.getvalue()
