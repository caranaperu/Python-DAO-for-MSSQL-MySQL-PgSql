from carlib.utils import cls_locked_attrs

@cls_locked_attrs
class A:
    def __init__(self):
        self._a = 0

a = A()
a._a = 1
#a.b = 2

class B(A):
    def __init__(self):
        A.__init__(self)
        self._c = 0
        self._d = 0

b = B()
b._c = 1
b._d = 2
#b.test = 3
print(b._c)

import sys

sys.path.insert(0, '/home/carana/PycharmProjects/test')

from Model import Model

class MainTableModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.id_key = None
        self.anytext = None

    def is_pk_uid(self):
        return True

    def get_pk_fields(self):
        return ('id_key',)

    # retornar None si no se desea chequeo de version
    def get_record_version_field(self):
        return 'updated_when'

def func1(classType):
    c = classType()
    c.id_key = 100
    print(c.__dict__)

func1(MainTableModel)