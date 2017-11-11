from inspect import stack


def cls_locked_attrs(cls):
    def locked_set_attr(self, key, value):
        if not hasattr(self, key) and stack()[1][3] != "__init__":
            raise AttributeError("Class {} is frozen. Cannot set {} = {}"
                                 .format(cls.__name__, key, value))
        else:
            # Inicialmente se accesaba via el diccionarion , pero esto hace que no
            # se invoque el setattr y en el caso que existan decoradores para validacion
            # estos no seira invocados.
            #       self.__dict__[key] = value
            # esta ocion es valida si no se desea que se accese via setter el cual
            # no es el caso.
            #print(cls)
            #print(key)
            #print(value)
            super(cls,self).__setattr__(key, value)

    cls.__setattr__ = locked_set_attr
    return cls
