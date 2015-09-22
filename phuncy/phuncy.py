from copy import copy
import inspect

from thunctor import Thunk, unroll

def curry(f):
    arg_spec = inspect.getargspec(f)
    assert not arg_spec.varargs
    assert not arg_spec.keywords
    arg_count = len(arg_spec.args)
    def currier(stashed_args):
        def curried(*args):
            stashed_args.extend(args)
            assert len(stashed_args) <= arg_count
            if len(stashed_args) == arg_count:
                return f(*stashed_args)
            else:
                return currier(stashed_args)
        return curried
    def gen(*args, **kwargs):
        return currier([])(*args, **kwargs)
    return gen

def test(a, b, c):
    return [a, b, c]

def test2(a, b):
    return [a, b]

assert curry(test)(1, 2)(3) == [1,2,3]
assert curry(test2)(1)(2) == [1,2]

@curry
def head(xs):
    return xs.map(lambda xs: xs[0])

@curry
def tail(xs):
    return xs.map(lambda xs: xs[1:])

@curry
def match(x, p):
    return p(unroll(lambda me: x)())

@curry
def apply(f, xs):
    return f(*xs)

@curry
def fold(f, x, xs):
    if match(xs, lambda x: not x):
        return x
    else:
        return f(Thunk([f, x, tail(copy(xs))]).bind(apply(fold)),
                 head(copy(xs)))

@curry
def map(f, xs):
    return xs.map(lambda xs: map(f, xs))

@curry
def filter(f, xs):
    return xs.map(lambda xs: filter(f, xs))

def do(exp, **kwargs):
    load = Thunk({})
    def loadKeypair(k, v):
        return v.map(lambda v: {k: v})
    def apply(load, k, v):
        load.bind(lambda ls: loadKeypair(k, v).map(lambda p: dict(ls, **p)))
    for k, v in kwargs.iteritems():
        apply(load, k, v)
    return load.bind(lambda ls: exp(**ls))

@curry
def add(a, b):
    return do(lambda a, b: Thunk(a + b), a=a, b=b)

assert unroll(lambda me, a, b: add(a, b))(Thunk(1), Thunk(2)) == 3
assert unroll(lambda me: fold(add, Thunk(0), Thunk([1,2,3])))() == 6

