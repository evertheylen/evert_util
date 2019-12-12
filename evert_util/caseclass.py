 
import collections


class Property:
    def __init__(self, default=lambda: None):
        self.default = default


def classitems(dct, bases):
    """Helper function to allow for inheritance"""
    for b in bases:
        yield from classitems(getattr(b, '_props', b.__dict__), b.__bases__)
    yield from dct.items()
    

class MetaCaseClass(type):
    @classmethod
    def __prepare__(self, name, bases):
        # Thanks to http://stackoverflow.com/a/27113652/2678118
        return collections.OrderedDict()
    
    def __new__(self, name, bases, dct):
        props = collections.OrderedDict()
        for k, prop in classitems(dct, bases):
            if isinstance(prop, Property):
                props[k] = prop
        
        # For __slots__ support
        for k, prop in list(dct.items()):
            if isinstance(prop, Property):
                del dct[k]
        
        dct['_props'] = props
        dct['__slots__'] = tuple(props.keys())
        return type.__new__(self, name, bases, dict(dct))



class CaseClass(metaclass=MetaCaseClass):
    def __init__(self, *args, **kwargs):
        default_dct = {k: prop.default() for k, prop in self._props.items()}
        
        for val, (name, prop) in zip(args, self._props.items()):
            setattr(self, name, val)
            del default_dct[name]
            
        for k, val in kwargs.items():
            setattr(self, k, val)
            del default_dct[k]
        
        for k, val in default_dct.items():
            setattr(self, k, val)
    
    def __eq__(self, other):
        return type(self) == type(other) and all(getattr(self, k) == getattr(other, k) for k in self._props)
    
    def __repr__(self):
        return type(self).__name__ + "(" + ", ".join(f"{k}={getattr(self, k)}" for k in self._props) + ")"
    
    def __hash__(self):
        return hash(tuple(getattr(self, k) for k in self._props))
    
    def to_dict(self):
        return {k: getattr(self, k) for k in self._props}


if __name__ == '__main__':
    
    class Empty(CaseClass):
        pass
    
    class Foo(CaseClass):
        a = Property()
        b = Property()

    class Bar(Foo):
        c = Property()
    
    f = Foo(1, 2)
    print(f, type(f), type(f))
    b = Bar(1, 2, 3)
    bb = Bar(1, 2, 3)
    bbb = Bar(1, 4, 3)
    
    assert b == bb
    assert b != f
    print(b, bbb)
    assert b != bbb
    
    
    
