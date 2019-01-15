#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable(func):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """

    def wrapper(*args):
        update_wrapper(wrapper, func)
        return func(*args)

    update_wrapper(wrapper, func)
    return wrapper


def decorator(deco):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """

    def wrapper(*args):
        result = deco(*args)
        update_wrapper(wrapper, deco)
        return result

    update_wrapper(wrapper, deco)
    return wrapper


def countcalls(func):
    """Decorator that counts calls made to the function decorated."""

    def wrapper(*args):
        update_wrapper(wrapper, func)
        wrapper.calls += 1
        return func(*args)

    wrapper.calls = 0

    update_wrapper(wrapper, func)
    return wrapper


def memo(func):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """

    def wrapper(*args):
        update_wrapper(wrapper, func)

        if tuple(args) in wrapper.cache.keys():
            result = wrapper.cache[tuple(args)]
        else:
            result = func(*args)
            wrapper.cache[tuple(args)] = result
        return result

    wrapper.cache = {}

    update_wrapper(wrapper, func)
    return wrapper


def n_ary(func):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """

    def wrapper(*args):
        update_wrapper(wrapper, func)
        if len(args) > 2:
            return wrapper(args[0], wrapper(*args[1:]))
        else:
            return func(*args)

    update_wrapper(wrapper, func)
    return wrapper


def trace(indent_symbols):
    """Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    """

    def real_trace(func):
        def wrapper(*args):
            update_wrapper(wrapper, func)
            print indent_symbols * wrapper.indent, "--> {}({})".format(func.__name__, args[0])
            wrapper.indent += 1
            result = func(*args)
            wrapper.indent -= 1
            print indent_symbols * wrapper.indent, "<-- {}({}) == {}".format(func.__name__, args[0], result)
            return result

        wrapper.indent = 0
        # return update_wrapper(wrapper, func)
        update_wrapper(wrapper, func)
        return wrapper

    return real_trace


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n - 1) + fib(n - 2)


def main():
    print foo(4, 3)
    print foo(4, 3, 2)
    print foo(4, 3)
    print "foo was called", foo.calls, "times"

    print bar(4, 3)
    print bar(4, 3, 2)
    print bar(4, 3, 2, 1)
    print "bar was called", bar.calls, "times"

    print fib.__doc__
    fib(3)
    print fib.calls, 'calls made'


if __name__ == '__main__':
    main()
