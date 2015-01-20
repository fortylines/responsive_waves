# Copyright (c) 2015, Sebastien Mirolo
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

import json, logging, os

import vcd

from responsive_waves import settings

LOGGER = logging.getLogger(__name__)
BUFFER_SIZE = 4096


def _as_abspath(vcd_path, ext=None):
    '''Returns a pathname to a fixture for a VCD file.'''
    if ext and not vcd_path.endswith(ext):
        vcd_path = vcd_path + ext
    vcd_abspath = os.path.join(settings.FILESYS_STORAGE, vcd_path)
    if not os.path.exists(vcd_abspath):
        if getattr(settings, 'USE_FIXTURES', False):
            return os.path.join(settings.FIXTURE_DIRS[0],
                                os.path.basename(vcd_path))
    return vcd_abspath


class VCDFileBackend(object):

    def __init__(self):
        pass

    @staticmethod
    def load_variables(vcd_path):
        """
        Returns a scope tree (as a python dictionnary) of variables defined
        in *vcd_path*.
        """
        trace = vcd.Trace([], 0, 0, 1)
        vcd_abspath = _as_abspath(vcd_path, '.vcd')
        with open(vcd_abspath, 'rb') as vcd_file:
            buf = vcd_file.read(BUFFER_SIZE)
            while buf:
                bytes_used = trace.write(buf)
                if bytes_used != len(buf):
                    break
                buf = vcd_file.read(BUFFER_SIZE)
        data = str(trace)
        return json.loads(data)['definitions']

    @staticmethod
    def load_values(vcd_path, variables, start_time, end_time, resolution):
        '''
        Returns a json-formatted version of the time records
        for the VCD file pointed by *job_id*/*vcd_path*.
        '''
        LOGGER.debug("[load_values] %s %s [%ld, %ld[ at %d",
                     vcd_path, variables, start_time, end_time, resolution)
        trace = vcd.Trace(variables, start_time, end_time, resolution)
        vcd_abspath = _as_abspath(vcd_path, '.vcd')
        with open(vcd_abspath, 'rb') as vcd_file:
            buf = vcd_file.read(BUFFER_SIZE)
            while buf:
                bytes_used = trace.write(buf)
                if bytes_used != len(buf):
                    break
                buf = vcd_file.read(BUFFER_SIZE)
        # XXX It is kind of silly. We unserialize the JSON-encoded string
        #     *data* for the response to JSON-encode it again. I haven't
        #     found out how to avoid this (see: rest_framework/response.py:37)
        data = str(trace)
        return json.loads(data)

