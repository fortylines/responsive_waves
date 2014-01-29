# Copyright (c) 2012-2013, Fortylines LLC
#   All rights reserved.

import logging

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

LOGGER = logging.getLogger(__name__)

def load_backend(path):
    dot_pos = path.rfind('.')
    module, attr = path[:dot_pos], path[dot_pos + 1:]
    try:
        mod = import_module(module)
    except ImportError as err:
        raise ImproperlyConfigured('Error importing waveform backend %s: "%s"' % (path, err))
    except ValueError:
        raise ImproperlyConfigured('Error importing waveform backends. Is WAVEFORM_EXTRA_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" waveform backend' % (module, attr))
    return cls()


def get_backends():
    from responsive_waves import settings
    backends = []
    for backend_path in settings.WAVEFORM_BACKENDS:
        backends.append(load_backend(backend_path))
    return backends


def load_variables(waveform_id):
    """
    Returns a scope tree (as a python dictionnary) of variables defined
    in *waveform_id*.
    """
    scope = None
    for backend in get_backends():
        try:
            LOGGER.debug('try backend %s ...', backend.__class__.__name__)
            scope = backend.load_variables(waveform_id)
            if scope:
                break
        except (TypeError, IOError):
            # did not work, next one.
            continue
    return scope


def load_values(waveform_id, variables, start_time, end_time, resolution):
    """
    Returns a json-formatted version of the time records
    for the VCD file pointed by *job_id*/*vcd_path*.
    """
    values = None
    for backend in get_backends():
        try:
            LOGGER.debug('try backend %s ...', backend.__class__.__name__)
            values = backend.load_values(
                waveform_id, variables, start_time, end_time, resolution)
            if values:
                break
        except (TypeError, IOError):
            # did not work, next one.
            continue
    return values
