"""Modulo para soporte de decorators de validacion , basicamente para los Modelos
pero pueden ser usados en cualquier otra circunstancia si se desea.

Se incluyen funciones de soporte a los mismo , los cuales pueden tambien ser usados
libremente y son publicas,

Notes
-----
el decorator fv_allow_null no debe usarse con ninguno de los otros ya que este soporte
es directo en todos los demas validadores.

Los validadores empiezan con fv_ y deben ser usados solo como decorators, las funciones
de soporte empiezan con check_ y pueden ser usadas normalmente.

Debo indicar que los decoradores de validacion solo soportan decorar metodos con un solo
parametro , ya que como se indico estan creados con la intencion de usarse en los modelos
para la persistencia.

"""

import re

"""
    **********************************
    ************ Funciones de soporte
    **********************************
"""


def check_numeric_limit(new_value, limit_value, operation, allow_none=False):
    """
    Valida si un determinado numero se encuentra en el limite indicado por la operacion.

    Parameters
    ----------
    new_value: int or long or float
        El numero a validar.
    limit_value: int or long or float
        El valor limite a palicar la operacion a validar.
    operation: str
        Operacion de comparacion para validar.
        Las operaciones permitidas son:
            ">", ">=", "<", "<=", "="
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    bool
        True si es correcta la validacion , False de lo contrario

    Raises
    ------
    AttributeError
        Si el parametro limit_value no es ni int,long o float.
        Si el valor a validar new_value no es int,long o float.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el parametro operation indica una operacion no soportada.
    """
    if not isinstance(limit_value, (int, long, float)):
        raise AttributeError(
            'Invalid limit_value ({0} of type {1}), supported types are (int,long,float)'.format(limit_value,
                                                                                                 type(limit_value)))

    if new_value is None:
        if not allow_none:
            raise ValueError("Invalid new_value, None value is not allowed")
        else:
            return True
    elif not isinstance(new_value, (int, long, float)):
        raise AttributeError('Invalid Type only numeric allowed (int,long,float)')

    if operation == ">":
        if new_value <= limit_value:
            return False
    elif operation == ">=":
        if new_value < limit_value:
            return False
    elif operation == "<":
        if new_value >= limit_value:
            return False
    elif operation == "<=":
        if new_value > limit_value:
            return False
    elif operation == "=":
        if new_value != limit_value:
            return False
    else:
        raise ValueError("check_numeric_limit - Operation '{0}' not supported".format(operation))

    return True


def check_string_type(new_value, type_check, allow_none):
    """
    Valida si un determinado numero se encuentra en el limite indicado por la operacion.

    Parameters
    ----------
    new_value: str
        El string a validar.
    type_check: str
        Indica el tipo de validacion a efectuar.
        Las operaciones permitidas son:
            "isalpha","isalnum","isdigit"
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    bool
        True si es correcta la validacion , False de lo contrario

    Raises
    ------
    AttributeError
        Si el valor a validar new_value no es string.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el parametro type_check indica una tipo de validacion no soportada.
    """
    if new_value is None:
        if not allow_none:
            raise ValueError("Invalid new_value, None value is not allowed")
    elif not isinstance(new_value, str):
        raise AttributeError('Invalid new_value type , only string allowed')

    if type_check == 'isalpha':
        return new_value.isalpha()
    elif type_check == 'isalnum':
        return new_value.isalnum()
    elif type_check == 'isdigit':
        return new_value.isdigit()
    else:
        raise ValueError("check_string_type - type_check '{0}' not supported".format(type_check))


"""
    **********************************
    ******* Decorators para validacion
    **********************************
"""


def fv_num_minmax(min_value, max_value, allow_none=False):
    """
    Valida si un entero,long o float estan dentro de ciertos limites.

    Parameters
    ----------
    min_value: int,long,float
        El minimo valor valido.
    max_value: int,long,float
        El maximo valor valido.
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    int,long,float
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el parametro min_value es menor que max_value o alguno de ellos no son ni int,long o float.
        Si el valor a validar no es int,long o float.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el valor esta fuera del rango indicado por min_value,max_value

    """

    def validate(wrapped):
        if not isinstance(min_value, (int, long, float)) or not isinstance(max_value, (int, long, float)):
            raise AttributeError('fv_type_minmax min_value and max_value need to be an int, long or float')

        if max_value <= min_value:
            raise AttributeError('fv_type_minmax min_value need to be greater than max_value')

        def inner(new_value):
            if new_value is None:
                if not allow_none:
                    raise ValueError("Invalid new_value, None value is not allowed")
            elif not isinstance(new_value, (int, long, float)):
                raise AttributeError("fv_type_minmax only suport numeric types (int,long,float)")

            if new_value < min_value or new_value > max_value:
                raise ValueError(
                    'Invalid new_value "{0}" is out of range ({1},{2})'.format(new_value, min_value, max_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_greater_than(limit_value, allow_none=False):
    """
    Valida si un entero,long o float es mayor que un determinado valor.

    Parameters
    ----------
    limit_value: int,long,float
        El minimo valor valido.
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    int,long,float
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el parametro limit_value no es ni int,long o float.
        Si el valor a validar no es int,long o float.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el valor no es mayor que limit_value
        Si el valor a validar no es int,long o float.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_numeric_limit(new_value, limit_value, '>', allow_none):
                raise ValueError('The value {0} is not greater than {1}'.format(new_value, limit_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_greater_than_equal(limit_value, allow_none=False):
    """
    Valida si un entero,long o float es mayor o igual que un determinado valor.

    Parameters
    ----------
    limit_value: int,long,float
        El valor limite a verificar.
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    int,long,float
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el parametro limit_value no es ni int,long o float.
        Si el valor a validar no es int,long o float.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el valor no es mayor o igual que limit_value
        Si el valor a validar no es int,long o float.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_numeric_limit(new_value, limit_value, '>=', allow_none):
                raise ValueError('The value {0} is not greater than or equal to {1}'.format(new_value, limit_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_less_than(limit_value, allow_none=False):
    """
    Valida si un entero,long o float es menor que un determinado valor.

    Parameters
    ----------
    limit_value: int,long,float
        El valor limite a verificar.
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    int,long,float
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el parametro limit_value no es ni int,long o float.
        Si el valor a validar no es int,long o float.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el valor no es menor que limit_value
        Si el valor a validar no es int,long o float.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_numeric_limit(new_value, limit_value, '<', allow_none):
                raise ValueError('The value {0} is not less than {1}'.format(new_value, limit_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_less_than_equal(limit_value, allow_none=False):
    """
    Valida si un entero,long o float es menor o igual que un determinado valor.

    Parameters
    ----------
    limit_value: int,long,float
        El valor limite a verificar.
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    int,long,float
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el parametro limit_value no es ni int,long o float.
        Si el valor a validar no es int,long o float.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el valor no es menor o igual que limit_value
        Si el valor a validar no es int,long o float.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_numeric_limit(new_value, limit_value, '<=', allow_none):
                raise ValueError('The value {0} is not less than or equal to {1}'.format(new_value, limit_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_len(min_len, max_len, allow_none=False):
    """
    Valida si la longitud de un string esta en el rango solicitado.

    Parameters
    ----------
    min_len: int
        La longitud minima del string.
    max_len: int,long,float
        La longitud maxima del string.
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    str
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el parametro min_len o max_len no es int.
        Si min_len > max_len.
        Si el valor a validar no es str.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si la longitud del string no esta en el rango indicado.

    """

    def validate(wrapped):
        if not isinstance(min_len, int) or not isinstance(max_len, int):
            raise AttributeError('fv_len min_len and max_len need to be an int')
        if min_len >= max_len:
            raise AttributeError('fv_len min_len need to be less than max_len')

        def inner(new_value):
            if new_value is None:
                if not allow_none:
                    raise ValueError("Invalid new_value, None value is not allowed")
            elif not isinstance(new_value, str):
                raise AttributeError('Invalid new_value type , only string allowed')

            if len(new_value) < min_len or len(new_value) > max_len:
                raise ValueError(
                    'The len of new_value "{0}" is out of range ({1},{2})'.format(new_value, min_len, max_len))
            return wrapped(new_value)

        return inner

    return validate


def fv_isalpha(allow_none=False):
    """
    Valida si un string es totalmente alfabetico.

    Parameters
    ----------
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    str
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el valor a validar no es str.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el string contine caracteres no alfabeticos.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_string_type(new_value, 'isalpha', allow_none):
                raise ValueError('Invalid new_value "{0}" contain non alphabetic characters)'.format(new_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_isalphanum(allow_none=False):
    """
    Valida si un string es totalmente alfanumerico.

    Parameters
    ----------
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    str
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el valor a validar no es str.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el string contine caracteres no alfanumericos.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_string_type(new_value, 'isalnum', allow_none):
                raise ValueError('Invalid new_value "{0}" contain non alphanumeric characters)'.format(new_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_isdigit(allow_none=False):
    """
    Valida si un string es compuesto totalmente de numeros.

    Parameters
    ----------
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    str
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el valor a validar no es str.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el string contine caracteres no numericos.

    """

    def validate(wrapped):
        def inner(new_value):
            if not check_string_type(new_value, 'isdigit', allow_none):
                raise ValueError('Invalid new_value "{0}" contain non digit characters)'.format(new_value))
            return wrapped(new_value)

        return inner

    return validate


def validate_with_regex(new_value, regex, allow_none):
    if new_value is None:
        if not allow_none:
            raise ValueError("Invalid new_value, None value is not allowed")
    elif not isinstance(new_value, str):
        raise AttributeError('Invalid new_value type , only string allowed')

    if re.match(regex, new_value) is not None:
        return True
    return False


def fv_is_email(allow_none=False):
    """
    Valida si un string representa un email validamente compuesto.

    Parameters
    ----------
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    str
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el valor a validar no es str.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el string no representa un email valido.

    """

    def validate(wrapped):
        def inner(new_value):
            if not validate_with_regex(new_value,
                                       "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                       allow_none):
                raise ValueError('Invalid new_value "{0}" is not a valid email)'.format(new_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_is_ipv4(allow_none=False):
    """
    Valida si un string representa una direccion ipv4 valida.

    Parameters
    ----------
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    str
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si el valor a validar no es str.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el string no representa un ipv4 valido.

    """

    def validate(wrapped):
        def inner(new_value):
            if not validate_with_regex(new_value,
                                       "^([1][0-9][0-9].|^[2][5][0-5].|^[2][0-4][0-9].|^[1][0-9][0-9].|^[0-9][0-9].|^[0-9].)([1][0-9][0-9].|[2][5][0-5].|[2][0-4][0-9].|[1][0-9][0-9].|[0-9][0-9].|[0-9].)([1][0-9][0-9].|[2][5][0-5].|[2][0-4][0-9].|[1][0-9][0-9].|[0-9][0-9].|[0-9].)([1][0-9][0-9]|[2][5][0-5]|[2][0-4][0-9]|[1][0-9][0-9]|[0-9][0-9]|[0-9])$",
                                       allow_none):
                raise ValueError('Invalid new_value "{0}" is not a valid ipv4)'.format(new_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_in_list(list_to_check, allow_none=False):
    """
    Valida si un valor cualquiera se encuentra en la lista.

    Parameters
    ----------
    list_to_check: list[any]
    allow_none: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    any
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    AttributeError
        Si list_to_check no es list.
    ValueError
        Si el valor es None y no esta permitido (allow_none = False)
        Si el valor a evaluar no se encuentra en la lista list_to_check.

    """

    def validate(wrapped):
        if not isinstance(list_to_check, list) or isinstance(list_to_check, str):
            raise AttributeError('fv_in_list list_to_ckeck need to be a list')

        def inner(new_value):
            if new_value is None:
                if not allow_none:
                    raise ValueError("Invalid new_value, None value is not allowed")

            if new_value not in list_to_check:
                raise ValueError('Invalid new_value "{0}" not in the list'.format(new_value))
            return wrapped(new_value)

        return inner

    return validate


def fv_allow_null(allow=False):
    """
    Valida si el valor admite None como valido.

    Parameters
    ----------
    allow: bool, optional
        Chequear si el valor None es valido.

    Returns
    -------
    any or None
        Con el valor validado si la validacion es correcta.

    Raises
    ------
    ValueError
        Si el valor es None y no esta permitido (allow = False)

    """

    def validate(wrapped):
        def inner(new_value):
            if new_value is None:
                if not allow:
                    raise ValueError("Invalid new_value, None value is not allowed")
            return wrapped(new_value)

        return inner

    return validate


@fv_num_minmax(90, 99)
def doge(param):
    print('Es ok')


@fv_isdigit()
def doge2(param):
    print('Es ok')


@fv_is_email()
def check_email(param):
    print('Es ok')


# @fv_allow_null(False)
@fv_is_ipv4()
def check_ip(param):
    print('Es ok')


if __name__ == "__main__":
    print(check_numeric_limit(1200, 1300, ">"))
    print(check_numeric_limit(1400, 1300, ">"))
    print(check_numeric_limit(1400, 1400, ">="))
    print(check_numeric_limit(1401, 1400, ">="))
    print(check_numeric_limit(1399, 1400, ">="))

    print("**************************************")

    print(check_numeric_limit(1200.00, 1300, "<"))
    print(check_numeric_limit(1400, 1300, "<"))
    print(check_numeric_limit(1400.01, 1400, "<="))
    print(check_numeric_limit(1401, 1400, "<="))
    print(check_numeric_limit(1399, 1400, "<="))

    print("**************************************")

    # doge(-14)

    doge2("1234")

    s = u"1234"
    print(s.isdecimal())

    print("**************************************")
    check_email('aranape@gmail.com')
    check_ip('192.168.0.1')
    check_ip(None)
    print("**************************************")


    def in_list(new_value, list):
        if new_value in list:
            return True
        else:
            return False


    a = ["a", 1, "dos"]
    print(in_list("b", a))
    print(in_list(1, a))
    print(in_list("dos", a))
