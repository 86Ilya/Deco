#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable(func):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """

    return func


def decorator(deco):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """

    def wrapper_for_deco(deco_args):

        if hasattr(deco_args, '__call__'):
            func = deco_args
            # Если на вход пришла ф-ия, то обернём её декоратором deco
            resulted_func = deco(func)
            # Обновим словари нашей ф-ии словарями ф-ии извне
            update_wrapper(resulted_func, func)

            # Обёртка для результирующей ф-ии
            def wrapped_func(*args):
                # Каждый раз при запуске будем обновлять наши словари
                update_wrapper(resulted_func, func)
                result = resulted_func(*args)
                # Так же обновим словари нашей обёртки словарями результирующей ф-ии
                update_wrapper(wrapped_func, resulted_func)
                return result

            update_wrapper(wrapped_func, func)
            return wrapped_func

        else:
            # В случае, если на вход пришла не ф-ия, значит у нас декоратор с аргументами
            # Поэтому вначале получим декортатор.

            new_deco = deco(deco_args)

            def wrapper_for_wrapped_func(func):
                resulted_func = new_deco(func)
                update_wrapper(resulted_func, func)

                def wrapped_func(*args):
                    update_wrapper(resulted_func, func)
                    result = resulted_func(*args)
                    update_wrapper(wrapped_func, resulted_func)
                    return result

                update_wrapper(wrapped_func, func)
                return wrapped_func

            return wrapper_for_wrapped_func

    return wrapper_for_deco


@decorator
def countcalls(func):
    """Decorator that counts calls made to the function decorated."""

    def wrapper(*args):
        result = func(*args)
        wrapper.calls += 1
        return result

    wrapper.calls = 0

    return wrapper


@decorator
def memo(func):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """

    def wrapper(*args):
        if args in wrapper.cache.keys():
            result = wrapper.cache[args]
        else:
            result = func(*args)
            wrapper.cache[args] = result
        return result

    wrapper.cache = {}

    return wrapper


@decorator
def n_ary(func):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """

    def wrapper(*args):
        if len(args) > 2:
            return wrapper(args[0], wrapper(*args[1:]))
        elif len(args) == 1:
            return args
        else:
            return func(*args)

    return wrapper


@decorator
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
            print indent_symbols * wrapper.indent, "--> {}({})".format(func.__name__, args[0])
            wrapper.indent += 1
            result = func(*args)
            wrapper.indent -= 1
            print indent_symbols * wrapper.indent, "<-- {}({}) == {}".format(func.__name__, args[0], result)
            return result

        wrapper.indent = 0
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
