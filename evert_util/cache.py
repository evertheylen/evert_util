
import os
import pickle
import hashlib
from functools import wraps
from itertools import chain
from collections import defaultdict

def str_hash(*a):
    return hashlib.md5(str(a).encode()).hexdigest()

def rec_defaultdict():
    return defaultdict(rec_defaultdict)

def no_cache_input(obj):
    "marks an object or class to not be included as input for the cache"
    obj.__no_cache = None
    return obj

class DiskCache:
    instances = []
    
    @classmethod
    def save_all(cls):
        for i in cls.instances:
            i.save()
    
    def __init__(self, name):
        self.name = name
        self.changed = False
        self.loaded = False
        self.names = set()
        type(self).instances.append(self)
    
    @property
    def filename(self):
        return "cache/" + self.name + ".pickle"
    
    def load(self):
        if self.loaded:
            return
        
        if os.path.isfile(self.filename):
            with open(self.filename, "rb") as f:
                print("--- Loading ", self.filename, end="...", flush=True)
                self.dct = pickle.load(f)
                print(" done.")
        else:
            print("--- Couldn't find {}, starting fresh".format(self.filename))
            self.dct = rec_defaultdict()
        
        self.loaded = True
    
    def unload(self):
        self.save()
        self.loaded = False
        delattr(self, "dct")
    
    def save(self):
        if self.loaded and self.changed:
            if not os.path.isdir("cache"):
                os.makedirs("cache")
            
            with open(self.filename, "wb") as f:
                print("--- Saving", self.filename)
                pickle.dump(self.dct, f)
    
    def contains(self, current, inp):
        for i in inp:
            if i not in current:
                return False
            current = current[i]
        return True
    
    def set(self, current, inp, value):
        for i in inp[:-1]:
            current = current[i]
        current[inp[-1]] = value
    
    def get(self, current, inp):
        for i in inp[:-1]:
            current = current[i]
        return current[inp[-1]]
    
    # used as wrapper
    def __call__(self, func):
        self.names.add(func.__name__)
        
        @wraps(func)
        def cached_func(*args, **kwargs):
            self.load()
            d = self.dct[func.__name__]
            inp = []
            for a in chain(args, (kwargs[k] for k in sorted(kwargs.keys()))):
                if not hasattr(a, "__no_cache"):
                    inp.append(a.cache_identity if hasattr(a, "cache_identity") else a)
            
            if self.contains(d, inp):
                return self.get(d, inp)
            else:
                output = func(*args, **kwargs)
                self.set(d, inp, output)
                self.changed = True
                return output
        return cached_func


def lazyprop(fn):
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyprop
    
