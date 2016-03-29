# Copyright (c) 2016, Sebastien Mirolo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured


LOGGER = logging.getLogger(__name__)

def load_backend(path):
    dot_pos = path.rfind('.')
    module, attr = path[:dot_pos], path[dot_pos + 1:]
    try:
        mod = import_module(module)
    except ImportError as err:
        raise ImproperlyConfigured(
            'Error importing waveform backend %s: "%s"' % (path, err))
    except ValueError:
        raise ImproperlyConfigured('Error importing waveform backends.'\
            ' Is WAVEFORM_EXTRA_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define '\
            'a "%s" waveform backend' % (module, attr))
    return cls()


def get_backends():
    from responsive_waves import settings
    backends = []
    for backend_path in settings.WAVEFORM_BACKENDS:
        try:
            backend = load_backend(backend_path)
            backends.append(backend)
        except ImproperlyConfigured as err:
            LOGGER.warning('Unable to load backend %s: %s', backend_path, err)
            raise
    return backends


def load_variables(key):
    """
    Returns a scope tree (as a python dictionnary) of variables defined
    in *key*.
    """
    scope = None
    for backend in get_backends():
        try:
            LOGGER.debug('try backend %s ...', backend.__class__.__name__)
            scope = backend.load_variables(key)
            if scope:
                break
        except (TypeError, IOError):
            # did not work, next one.
            continue
    return scope


def load_values(key, variables, start_time, end_time, resolution):
    """
    Returns a json-formatted version of the time records
    for the VCD file pointed by *job_id*/*vcd_path*.
    """
    values = None
    for backend in get_backends():
        try:
            LOGGER.debug('try backend %s ...', backend.__class__.__name__)
            values = backend.load_values(
                key, variables, start_time, end_time, resolution)
            if values:
                break
        except (TypeError, IOError):
            # did not work, next one.
            continue
    return values


def retrieve_log(key):
    """
    Returns a log output from its key.
    """
    log_content = None
    for backend in get_backends():
        try:
            LOGGER.debug('try backend %s ...', backend.__class__.__name__)
            log_content = backend.retrieve(key)
            if log_content:
                break
        except (TypeError, IOError):
            # did not work, next one.
            continue
    return log_content
