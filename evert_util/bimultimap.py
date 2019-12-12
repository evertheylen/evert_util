
import itertools


class NotFlat(ValueError):
    def __init__(self, v):
        super().__init__(f"Could not flatten the items {v}")


class biset(set):
    def __init__(self, *args, _inverse_map, _key, **kwargs):
        self.inverse = _inverse_map
        self.key = _key
        super().__init__(*args, **kwargs)
    
    def update(self, *others):
        for other in others:
            self.__ior__(other)
    
    def __ior__(self, other):
        if isinstance(other, set):
            to_add = other - self
            super().__ior__(to_add)
            for el in to_add:
                set.add(self.inverse[el], self.key)
        else:
            for el in other:
                self.add(el)
        return self
    
    def intersection_update(self, *others):
        for other in others:
            self.__iand__(other)
    
    def __iand__(self, other):
        assert isinstance(other, set)
        to_remove = self - other
        self.__isub__(to_remove)
        return self
    
    def difference_update(self, *others):
        for other in others:
            self.__isub__(other)
    
    def __isub__(self, to_remove):
        assert isinstance(to_remove, set)
        super().__isub__(to_remove)
        for el in to_remove:
            set.discard(self.inverse[el], self.key)
        return self
    
    # TODO symmetric_difference_update
    
    def add(self, elem):
        super().add(elem)
        set.add(self.inverse[elem], self.key)
    
    def remove(self, elem):
        super().remove(elem)
        set.remove(self.inverse[elem], self.key)
    
    def discard(self, elem):
        super().discard(elem)
        set.discard(self.inverse[elem], self.key)
    
    def pop(self):
        elem = super().pop()
        set.remove(self.inverse[elem], elem)
        return elem

    def clear(self):
        for elem in self:
            set.remove(self.inverse[elem], self.key)
        super().clear()



class BiMultiMap:
    def __init__(self, iterable=(), *, _inverse=None, **kwargs):
        if _inverse is None:
            self.inverse = BiMultiMap(_inverse=self)
        else:
            self.inverse = _inverse
        self.data = {}
        if isinstance(iterable, dict):
            iterable = iterable.items()
        for k, v in itertools.chain(iterable, kwargs.items()):
            self[k] = v
    
    def _newset(self, k, iterable=()):
        return biset(iterable, _inverse_map=self.inverse, _key=k)
    
    def __getitem__(self, k):
        if k not in self.data:
            v = self.data[k] = self._newset(k)
            return v
        else:
            return self.data[k]
    
    def __setitem__(self, k, vals):
        if k in self.data:
            # remove existing data in inverse
            for v in self.data[k]:
                self.inverse.data[v].remove(k)
        self.data[k] = self._newset(k, vals)
        for v in vals:
            if v in self.inverse.data:
                self.inverse.data[v].add(k)
            else:
                self.inverse.data[v] = self.inverse._newset(v, (k,))
    
    def __delitem__(self, k):
        for v in self.data[k]:
            set.remove(self.inverse.data[v], k)
        del self.data[k]
    
    def __contains__(self, k):
        return k in self.data
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)
    
    def clear(self):
        self.data.clear()
        self.inverse.data.clear()
    
    def get(self, *args, **kwargs):
        return self.data.get(*args, **kwargs)
    
    def items(self):
        return self.data.items()
    
    def values(self):
        return self.data.values()
    
    def keys(self):
        return self.data.keys()
    
    # TODO pop, popitem, setdefault?
    
    def update(self, other):
        if isinstance(other, BiMultiMap):
            self.data.update(other.data)
            self.inverse.data.update(other.inverse.data)
        else:
            iterable = other.items() if isinstance(other, dict) else iter(other)
            for k, vals in iterable:
                self[k] = vals
    
    # Multimap stuff
    
    def contains_mapping(self, k, v):
        # redundant?
        return v in self.data.get(k, ())
    
    def flat_update(self, other):
        iterable = other.items() if isinstance(other, dict) else iter(other)
        for k, v in iterable:
            self[k].add(v)
    
    def flat_items(self):
        for k, values in self.data.items():
            for v in values:
                yield k, v
                
    def flat_values(self):
        for values in self.data.values():
            for v in values:
                yield v
    
    def flat_len(self):
        s = 0
        for v in self.data.values():
            s += len(v)
        return s
    
    def flatten(self):
        d = {}
        for k, v in self.get_left().items():
            if len(v) != 1:
                raise NotFlat(v)
            d[k] = v.pop()
        return d
    

if __name__ == '__main__':
    m = BiMultiMap()
    m['a'].add(1)
    m['b'].add(2)
    m['c'].add(2)
    m['d'] = [4]
    m['d'].add(5)
    m.inverse[4].add('a')
    assert m.data == {'a': {1, 4}, 'b': {2}, 'c': {2}, 'd': {4,5}}
    assert m.inverse.data == {1: {'a'}, 2: {'b', 'c'}, 4: {'d', 'a'}, 5: {'d'}}
