from inspect import stack

def cls_locked_attrs(cls):

    def locked_set_attr(self, key, value):
        if not hasattr(self, key) and stack()[1][3] != "__init__":
            raise AttributeError("Class {} is frozen. Cannot set {} = {}"
                  .format(cls.__name__, key, value))
        else:
            self.__dict__[key] = value

    cls.__setattr__ = locked_set_attr
    return cls