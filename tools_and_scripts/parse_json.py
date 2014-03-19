#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Tool to parse a json string from command line by applying a 'formatter'
"""


import sys
import json


def extract_json(input):
    """ Parse json input string to a python object
    >>> extract_json('{}')
    {}
    >>> extract_json('{ "a": 1, "b":[2]}')
    {u'a': 1, u'b': [2]}

    >>> import sys; sys.stderr = sys.stdout
    >>> extract_json('not json_string')
    Traceback (most recent call last):
    ...
    SystemExit: 1
    """
    try:
        answer_dict = json.loads(input)
    except ValueError:
        print >> sys.stderr, 'Could not load JSON object from input.'
        sys.exit(1)
    return answer_dict


def get_formatter(args):
    """
    Extract a lambda from 'args[0]' where 'x' is the only parameter

        >>> get_formatter([])  # doctest: +ELLIPSIS,
        <function <lambda> at 0x...>



    If args is empty, an 'identity' lambda is returned

        >>> example = {'a':1, 'b':2}
        ...
        >>> get_formatter([])(example) == example
        True

        >>> get_formatter(["x['a']"])(example)
        1
        >>> get_formatter(["x['a']"])(example)
        1

    It's a lambda, and you can have fun with list comprehension

        >>> get_formatter(["[0 == (val % 2) for val in x.values()]"])(example)
        [False, True]
    """
    try:
        extract = args[0]
    except IndexError:
        extract = 'x'

    lambda_str = '(lambda x: %s)' % extract
    format_func = eval(lambda_str)
    return format_func


def _main(argv):  # pragma: no cover
    """
    Read a JSON on stdin and apply the given argument as a
        'lambda x: <lambda_arg>'
    """

    format_func = get_formatter(argv[1:])
    input = sys.stdin.read()
    json_dict = extract_json(input)

    value = format_func(json_dict)
    print value


if __name__ == '__main__':  # pragma: no cover
    _main(sys.argv)
