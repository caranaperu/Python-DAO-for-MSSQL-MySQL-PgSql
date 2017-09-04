from DAOConstraints import *

class SqlHelper(object):
    @staticmethod
    def generate_sql_statement(sql_string, c_constraints):
        # type: (str, DAOConstraints) -> str
        for i, (field, operator) in enumerate(c_constraints.filter_fields.items()):
            find_patterns = ("$f_" + field, "$f_" + str(i), "$ff_" + field, "$ff_" + str(i))

            field_value = c_constraints.get_filter_field_value(field)
            for j, to_find in enumerate(find_patterns):
                if (j < 2):
                    if (isinstance(field_value, str)):
                        sql_string = sql_string.replace(to_find, field + " " +
                                operator.value + " '" + field_value + "'")
                    elif (field_value is None):
                        if (operator == DAOConstraints.FilterType.EQUAL):
                            sql_string = sql_string.replace(to_find, field + " is null")
                        else:
                            sql_string = sql_string.replace(to_find, field + " is not null")
                    elif (operator == DAOConstraints.FilterType.PARTIAL or
                        operator == DAOConstraints.FilterType.IPARTIAL):
                        sql_string = sql_string.replace(to_find, field + " " +
                                    operator.value + " '%" + str(field_value) + "%'")
                    else:
                        sql_string = sql_string.replace(to_find, field + " " +
                                    operator.value + " " + str(field_value))
                else:
                    sql_string = sql_string.replace(to_find,field)

        # busqueda de campos para order by
        for i, (field, direction) in enumerate(c_constraints.sort_fields.items()):
            to_find = "$o" + str(i)
            if (sql_string.find(to_find) >= 0):
                sql_string = sql_string.replace(to_find, field + " " + str(direction))

        return sql_string

if __name__ == "__main__":
    import mem_profile
    import time

    print ('Memory (Before): {}Mb'.format(mem_profile.memory_usage_psutil()))

    daoc = DAOConstraints()
    daoc.add_sort_field('xxd1', DAOConstraints.SortType.DESC)
    daoc.add_sort_field('xxd', DAOConstraints.SortType.ASC)
    daoc.add_sort_field('ssss', DAOConstraints.SortType.ASC)
    daoc.add_sort_field('555', DAOConstraints.SortType.ASC)

    daoc.add_filter_field('field_1', 3, DAOConstraints.FilterType.EQUAL)
    daoc.add_filter_field('field_2', "soy el field1",
                          DAOConstraints.FilterType.EQUAL)
    daoc.add_filter_field('field_22', "No soy el field1",
                          DAOConstraints.FilterType.NO_EQUAL)
    daoc.add_filter_field(
        'fiel_3', 100.00, DAOConstraints.FilterType.GREAT_THAN)
    daoc.add_filter_field(
        'fiel_31', 100.00, DAOConstraints.FilterType.LESS_THAN_EQ)
    daoc.add_filter_field(
        'fiel_32', 100.00, DAOConstraints.FilterType.NO_EQUAL)

    daoc.add_filter_field('fiel_4', None, DAOConstraints.FilterType.NO_EQUAL)
    daoc.add_filter_field('fiel_5', None, DAOConstraints.FilterType.EQUAL)
    print ('Memory (After) : {}Mb'.format(mem_profile.memory_usage_psutil()))

    s = """select * from table t1
    inner join tb_table2 t2 on t2.$ff_fiel_32 = t1.$ff_fiel_32
    where $f_fiel_32 and $f_1 and $f_2 or ($f_fiel_3 and $f_4) and ($f_5 and $f_6 and $f_7 and $f_field_22)
    order by $o0,$o1"""

    memb = mem_profile.memory_usage_psutil()
    print ('Memory (Before): {}Mb'.format(memb))

    t1 = time.clock()

    print(SqlHelper.generate_sql_statement(s,daoc))

    t2 = time.clock()

    memf = mem_profile.memory_usage_psutil()
    print ('Memory (After) : {}Mb'.format(memf))
    print ('Diff {} mem'.format(memf-memb))
    print ('Diff {} mem'.format(1024*(memf-memb)))
    print ('Took {} Seconds'.format(t2-t1))

    import cProfile, StringIO, pstats
    pr = cProfile.Profile()
    pr.enable()
    print(SqlHelper.generate_sql_statement(s,daoc))
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()