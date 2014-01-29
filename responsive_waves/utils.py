# Copyright (c) 2013, Fortylines LLC
#   All rights reserved.

"""Functions to filter variable sets."""

import logging, re

from responsive_waves.models import Browser, Variable

LOGGER = logging.getLogger(__name__)

# can't use . because of jquery, can't use / because of d3js
NODE_SEP = '/'


def paths_from_scope(scope, prefix=''):
    """
    Returns a list of paths from a scope tree implemented
    as a recursive dictionary of strings.
    """
    results = []
    for name, value in scope.iteritems():
        if prefix:
            full_path = prefix + NODE_SEP + name
        else:
            full_path = name
        if isinstance(value, dict):
            results += [ full_path + NODE_SEP ]
            results += paths_from_scope(value, full_path)
        else:
            results += [ full_path ]
    return results


def scope_filter(left, right):
    """
    Returns the scope left filtered by nodes belonging to right.
    """
    if isinstance(left, dict) and isinstance(right, dict):
        scope = {}
        for key in right.keys():
            if key in left:
                scope[key] = scope_filter(left[key], right[key])
        return scope
    else:
        return left


def variables_full_path(scope, prefix=''):
    """
    Returns a list of variable paths from root scope to local name
    given a tree of scopes and variables.
    """
    results = []
    for name, value in scope.iteritems():
        if prefix:
            full_path = prefix + NODE_SEP + name
        else:
            full_path = name
        if isinstance(value, basestring):
            results += [ Variable(path=full_path, is_leaf=True) ]
        else:
            results += variables_full_path(value, full_path)
    return results


def variables_at_scope(scope, prefix=''):
    """Returns a list of variables defined at an inner scope defined
    by prefix."""
    fullpath_variable_list = []
    if prefix:
        for root in prefix.split(NODE_SEP):
            scope = scope[root]
    for name, value in scope.iteritems():
        if prefix:
            fullpath = prefix + NODE_SEP + name
        else:
            fullpath = name
        is_leaf = isinstance(value, basestring)
        fullpath_variable_list += [ Variable(path=fullpath, is_leaf=is_leaf) ]
    return fullpath_variable_list


def add_scope(scope, var_nodes):
    if len(var_nodes) > 1:
        if not var_nodes[0] in scope:
            scope[var_nodes[0]] = {}
        add_scope(scope[var_nodes[0]], var_nodes[1:])
    elif len(var_nodes) == 1:
        scope[var_nodes[0]] = ""
    else:
        raise KeyError()


def variables_as_scope(variable_list):
    """
    Build a scope out of a list of variables.
    """
    scope = {}
    for var_path in variable_list:
        add_scope(scope, var_path.split(NODE_SEP))
    return scope


def leafs(scope, prefix=""):
    results = {}
    for name, value in scope.iteritems():
        if prefix:
            qualified_path = prefix + NODE_SEP + name
        else:
            qualified_path = name
        if isinstance(value, dict):
            next_leafs = leafs(value, qualified_path)
            for next_name, next_value in next_leafs.iteritems():
                if next_name in results:
                    results[next_name].append(next_value)
                else:
                    results[next_name] = next_value
        else:
            if value in results:
                results[value] += [ qualified_path ]
            else:
                results[value] = [ qualified_path ]
    return results


def leafs_match(scope, path_list):
    match_scope = variables_as_scope(path_list)
    return leafs(scope_filter(scope, match_scope))


def variables_match(regex, scope):
    """
    Returns a list of variable paths matching *regex*.
    """
    # XXX We should prune the scope tree directly globbing the relevent part
    # of *regex* as necessary instead of flatting the whole scope tree
    # and iterating through the list to prune the variable list.
    results = []
    for path in paths_from_scope(scope):
        look = re.match(regex, path)
        if look:
            results += [ Variable(path=path, is_leaf=path.endswith(NODE_SEP)) ]
    return results


def variables_root_prefixes(root_path):
    """
    Returns a list of (name, prefix) leading to root_path.
    """
    prefix = ''
    results = []
    for name in root_path.split(NODE_SEP):
        prefix = prefix + NODE_SEP + name
        results += [ (name, prefix) ]
    return results
