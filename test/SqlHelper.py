from carlib.persistence.Constraints import *


class SqlHelper(object):
    @staticmethod
    def generate_sql_statement(sql_string, c_constraints):
        # type: (str, DAOConstraints) -> str
        for i, (field, operator) in enumerate(c_constraints.filter_fields.items()):
            find_patterns = ("$f_" + field, "$f_" + str(i), "$ff_" + field, "$ff_" + str(i), "$fv_" + field)

            field_value = c_constraints.get_filter_field_value(field)
            for j, to_find in enumerate(find_patterns):
                if j < 2:
                    if (operator == Constraints.FilterType.PARTIAL or
                                operator == Constraints.FilterType.IPARTIAL):
                        sql_string = sql_string.replace(to_find, field + " " +
                                                        operator.value + " '%" + str(field_value) + "%'")
                    elif (isinstance(field_value, str)):
                        sql_string = sql_string.replace(to_find, field + " " +
                                                        operator.value + " '" + field_value + "'")
                    elif isinstance(field_value, bool):
                        sql_string = sql_string.replace(to_find, field + " " +
                                                        operator.value + " " + str(field_value))
                    elif (field_value is None):
                        if (operator == Constraints.FilterType.EQUAL):
                            sql_string = sql_string.replace(to_find, field + " is null")
                        else:
                            sql_string = sql_string.replace(to_find, field + " is not null")
                    else:
                        sql_string = sql_string.replace(to_find, field + " " +
                                                        operator.value + " " + str(field_value))
                elif j < 4:
                    sql_string = sql_string.replace(to_find, field)
                else:
                    sql_string = sql_string.replace(to_find, str(field_value))

        # busqueda de campos para order by
        for i, (field, direction) in enumerate(c_constraints.sort_fields.items()):
            to_find = "$o" + str(i)
            if (sql_string.find(to_find) >= 0):
                sql_string = sql_string.replace(to_find, field + " " + str(direction))

        # limits
        if c_constraints.limit:
            if (sql_string.find("$l_l") >= 0):
                sql_string = sql_string.replace("$l_l", str(c_constraints.limit))
        if c_constraints.offset:
            if (sql_string.find("$l_o") >= 0):
                sql_string = sql_string.replace("$l_o", str(c_constraints.offset))

        return sql_string


if __name__ == "__main__":
    import mem_profile
    import time

    print ('Memory (Before): {}Mb'.format(mem_profile.memory_usage_psutil()))

    daoc = Constraints()
    daoc.offset = 1000
    daoc.limit = 5000
    daoc.add_sort_field('nombres', Constraints.SortType.DESC)
    daoc.add_sort_field('apellidos', Constraints.SortType.ASC)

    daoc.add_filter_field('codigo', 3, Constraints.FilterType.EQUAL)
    daoc.add_filter_field(
        'monto', 100.00, Constraints.FilterType.NO_EQUAL)
    daoc.add_filter_field('apellidos', "arana reategui",
                          Constraints.FilterType.EQUAL)
    daoc.add_filter_field('nombres', "carlos alberto",
                          Constraints.FilterType.PARTIAL)
    daoc.add_filter_field(
        'sueldo', 100.00, Constraints.FilterType.GREAT_THAN)
    daoc.add_filter_field(
        'cts', 100.00, Constraints.FilterType.LESS_THAN_EQ)
    daoc.add_filter_field(
        'boolfield', "Y", Constraints.FilterType.EQUAL)
    daoc.add_filter_field('padre', None, Constraints.FilterType.NO_EQUAL)
    daoc.add_filter_field('madre', None, Constraints.FilterType.EQUAL)
    print ('Memory (After) : {}Mb'.format(mem_profile.memory_usage_psutil()))

    s = """select * from table t1
    inner join tb_table2 t2 on t2.$ff_codigo = t1.$ff_codigo
    where $f_cts and $f_1 and $f_2 or ($f_sueldo and $f_4) and ($f_5 and $f_6 and $f_7 and $f_nombres)
    and $ff_cts > $fv_cts and $f_boolfield
    order by $o0,$o1
    limit $l_l offset $l_o"""

    memb = mem_profile.memory_usage_psutil()
    print ('Memory (Before): {}Mb'.format(memb))

    t1 = time.clock()

    print(SqlHelper.generate_sql_statement(s, daoc))

    t2 = time.clock()

    memf = mem_profile.memory_usage_psutil()
    print ('Memory (After) : {}Mb'.format(memf))
    print ('Diff {} mem'.format(memf - memb))
    print ('Diff {} mem'.format(1024 * (memf - memb)))
    print ('Took {} Seconds'.format(t2 - t1))

    import cProfile, StringIO, pstats

    pr = cProfile.Profile()
    pr.enable()
    print(SqlHelper.generate_sql_statement(s, daoc))
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
