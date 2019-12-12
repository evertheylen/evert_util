
class GeneratorLength:
    def __init__(self, g, l):
        self.g = g
        self.l = l
    
    def __iter__(self):
        return self.g
    
    def __len__(self):
        return self.l
    
    def __getattr__(self, item):
        return getattr(self.g, item)


def generator_length(_len_func):
    def decorator(func, len_func=_len_func):
        @wraps(func)
        def wrapper(*a, **kw):
            gen = func(*a, **kw)
            return GeneratorLength(gen, len_func(*a, **kw))
        return wrapper
    return decorator
