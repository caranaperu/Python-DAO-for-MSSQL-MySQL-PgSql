class MetaConst(type):
    def __getattr__(cls, key):
        print("paso 01")
        return cls[key]

    def __setattr__(cls, key, value):
        print("paso 02")
        raise TypeError


class ConstantsDef(object):
    __metaclass__ = MetaConst
