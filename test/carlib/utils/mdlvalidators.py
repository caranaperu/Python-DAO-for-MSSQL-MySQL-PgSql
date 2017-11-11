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

Para el caso de su uso en los modelos hay que indicar que debe tenerse un orden estricto
si los atributos del modelo es accesado via properties, los setters deben ir al co,mienzo de
la lista y los validadores postriormente.

Por ejemplo :

class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.__c_bpartner_id = None
        self.__c_groupdoc_id = None
        self.__docaction = None
        self.issotrx = None

    @property
    def c_bpartner_id(self):
        return self.__c_bpartner_id

    @c_bpartner_id.setter
    @fv_num_minmax(0,1009999)
    def c_bpartner_id(self, partner_id):
        self.__c_bpartner_id =partner_id

    @property
    def c_groupdoc_id(self):
        return self.__c_groupdoc_id

    @c_groupdoc_id.setter
    @fv_less_than_equal(1000000000)
    def c_groupdoc_id(self, groupdoc_id):
        self.__c_groupdoc_id = groupdoc_id

    @property
    def docaction(self):
        return self.__docaction

    @docaction.setter
    @fv_len(1,2)
    @fv_allow_null()
    def docaction(self, docaction):
        self.__docaction = docaction

    def get_pk_fields(self):
        return None


Examples
--------
@fv_num_minmax(90, 99)
def min_max_test(param):
    print('min_max for {0} passed'.format(param))


@fv_isdigit()
def isdigit_test(param):
    print('isdigit for {0} passed').format(param)


@fv_is_email()
def email_check(param):
    print('is_email for {0} passed'.format(param))

@fv_is_ipv4()
def ipv4_check(param):
    print('is_ipv4 for {0} passed'.format(param))

@fv_in_list([100,"abc","c",1000])
def inlist_check(param):
    print('in_list for {0} passed'.format(param))


print(check_numeric_limit(1200, 1300, ">"))
print(check_numeric_limit(1400, 1300, ">"))
print(check_numeric_limit(1400, 1400, ">="))
print(check_numeric_limit(1401, 1400, ">="))
print(check_numeric_limit(1399, 1400, ">="))

print(check_numeric_limit(1200.00, 1300, "<"))
print(check_numeric_limit(1400, 1300, "<"))
print(check_numeric_limit(1400.01, 1400, "<="))
print(check_numeric_limit(1401, 1400, "<="))
print(check_numeric_limit(1399, 1400, "<="))

try:
    min_max_test(-14)
except ValueError as ex:
    print(ex.message)

try:
    min_max_test(80)
except ValueError as ex:
    print(ex.message)

min_max_test(90)
min_max_test(99)

isdigit_test("1234")
try:
    isdigit_test("-1234")
except ValueError as ex:
    print(ex.message)


email_check('aranape@gmail.com')
ipv4_check('192.168.0.1')
try:
    ipv4_check(None)
except ValueError as ex:
    print(ex.message)

inlist_check(1000)
try:
    inlist_check("dd")
except ValueError as ex:
    print(ex.message)


La salida de estos ejemplos seria:

False
True
True
True
False
True
False
False
False
True
Invalid new_value "-14" is out of range (90,99)
Invalid new_value "80" is out of range (90,99)
min_max for 90 passed
min_max for 99 passed
isdigit for 1234 passed
Invalid new_value "-1234" contain non digit characters
is_email for aranape@gmail.com passed
is_ipv4 for 192.168.0.1 passed
Invalid new_value, None value is not allowed
in_list for 1000 passed
Invalid new_value "dd" not in the list

"""

import re
from functools import wraps

from decimal import Decimal

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
    limit_value: int or long or float or Decimal
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
    if not isinstance(limit_value, (int, long, float, Decimal)):
        raise AttributeError(
            'Invalid limit_value ({0} of type {1}), supported types are (int,long,float,Decimal)'.format(limit_value,
                                                                                                         type(
                                                                                                             limit_value)))

    if new_value is None:
        if not allow_none:
            raise ValueError("Invalid new_value, None value is not allowed")
        else:
            return True
    elif not isinstance(new_value, (int, long, float, Decimal)):
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


def validate_with_regex(new_value, regex, allow_none):
    if new_value is None:
        if not allow_none:
            raise ValueError("Invalid new_value, None value is not allowed")
    elif not isinstance(new_value, str):
        raise AttributeError('Invalid new_value type , only string allowed')

    if re.match(regex, new_value) is not None:
        return True
    return False


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
    if not isinstance(min_value, (int, long, float)) or not isinstance(max_value, (int, long, float)):
        raise AttributeError('fv_type_minmax min_value and max_value need to be an int, long or float')

    if max_value <= min_value:
        raise AttributeError('fv_type_minmax min_value need to be greater than max_value')

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if value is None:
                if not allow_none:
                    raise ValueError("Invalid new_value, None value is not allowed")

            if value < min_value or value > max_value:
                raise ValueError(
                    'Invalid new_value "{0}" is out of range ({1},{2})'.format(value, min_value, max_value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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
    int,long,float,Decimal
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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_numeric_limit(value, limit_value, '>', allow_none):
                raise ValueError('The value {0} is not greater than {1}'.format(value, limit_value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_numeric_limit(value, limit_value, '>=', allow_none):
                raise ValueError('The value {0} is not greater than or equal to {1}'.format(value, limit_value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_numeric_limit(value, limit_value, '<', allow_none):
                raise ValueError('The value {0} is not less than {1}'.format(value, limit_value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_numeric_limit(value, limit_value, '<=', allow_none):
                raise ValueError('The value {0} is not less than or equal to {1}'.format(value, limit_value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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
    if not isinstance(min_len, int) or not isinstance(max_len, int):
        raise AttributeError('fv_len min_len and max_len need to be an int')
    if min_len > max_len:
        raise AttributeError('fv_len min_len need to be less than max_len')

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if value is None:
                if not allow_none:
                    raise ValueError("Invalid new_value, None value is not allowed")
            elif not isinstance(value, str):
                raise AttributeError('Invalid new_value type , only string allowed')

            if len(value) < min_len or len(value) > max_len:
                raise ValueError(
                    'The len of new_value "{0}" is out of range ({1},{2})'.format(value, min_len, max_len))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_string_type(value, 'isalpha', allow_none):
                raise ValueError('Invalid new_value "{0}" contain non alphabetic characters'.format(value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_string_type(value, 'isalnum', allow_none):
                raise ValueError('Invalid new_value "{0}" contain non alphanumeric characters'.format(value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not check_string_type(value, 'isdigit', allow_none):
                raise ValueError('Invalid new_value "{0}" contain non digit characters'.format(value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

    return validate


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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not validate_with_regex(value,
                                       "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                       allow_none):
                raise ValueError('Invalid new_value "{0}" is not a valid email)'.format(value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if not validate_with_regex(value,
                                       "^([1][0-9][0-9].|^[2][5][0-5].|^[2][0-4][0-9].|^[1][0-9][0-9].|^[0-9][0-9].|^[0-9].)([1][0-9][0-9].|[2][5][0-5].|[2][0-4][0-9].|[1][0-9][0-9].|[0-9][0-9].|[0-9].)([1][0-9][0-9].|[2][5][0-5].|[2][0-4][0-9].|[1][0-9][0-9].|[0-9][0-9].|[0-9].)([1][0-9][0-9]|[2][5][0-5]|[2][0-4][0-9]|[1][0-9][0-9]|[0-9][0-9]|[0-9])$",
                                       allow_none):
                raise ValueError('Invalid new_value "{0}" is not a valid ipv4)'.format(value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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
    if not isinstance(list_to_check, list) or isinstance(list_to_check, str):
        raise AttributeError('fv_in_list list_to_ckeck need to be a list')

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if value is None:
                if not allow_none:
                    raise ValueError("Invalid new_value, None value is not allowed")

            if value not in list_to_check:
                raise ValueError('Invalid new_value "{0}" not in the list'.format(value))

            retval = func(*args, **kwargs)
            return retval

        return wrapper

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

    def validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1]
            if value is None:
                if not allow:
                    raise ValueError("Invalid new_value, None value is not allowed")

            retval = func(*args, **kwargs)
            return retval

        return wrapper

    return validate
