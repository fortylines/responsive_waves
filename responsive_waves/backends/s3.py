# Copyright (c) 2015, DjaoDjin inc.
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

import boto
import vcd

from responsive_waves import settings

LOGGER = logging.getLogger(__name__)
BUFFER_SIZE = 4096


class VCDS3Backend(object):

    def __init__(self):
        self.conn = boto.connect_s3()
        remote_location = settings.SIMTRACE_STORAGE
        self.bucket = self.conn.get_bucket(remote_location[5:])

    @staticmethod
    def read(key, start=0):
        LOGGER.debug("GET [%d, %d] from key %s in S3 bucket %s",
            start, start + BUFFER_SIZE, key.name, key.bucket)
        return key.get_contents_as_string(
            headers={'Content-Range': 'bytes %d-%d/*' % (start, start + BUFFER_SIZE)})

    def load_variables(self, vcd_path):
        """
        Returns a scope tree (as a python dictionnary) of variables defined
        in *vcd_path*.
        """
        trace = vcd.Trace([], 0, 0, 1)
        key = self.bucket.get_key(vcd_path + '.vcd')
        bytes_used = 1
        buf_idx = 0
        buf = []
        while buf_idx < key.size and bytes_used != len(buf):
            buf = self.read(key, start=buf_idx)
            bytes_used = trace.write(buf)
            buf_idx += len(buf)
        data = str(trace)
        return json.loads(data)['definitions']

    def load_values(self, vcd_path, variables, start_time, end_time, resolution):
        '''
        Returns a json-formatted version of the time records
        for the VCD file pointed by *job_id*/*vcd_path*.
        '''
        LOGGER.debug("[load_values] %s %s [%ld, %ld[ at %d",
                     vcd_path, variables, start_time, end_time, resolution)
        trace = vcd.Trace(variables, start_time, end_time, resolution)
        key = self.bucket.get_key(vcd_path + '.vcd')
        bytes_used = 1
        buf_idx = 0
        buf = []
        while buf_idx < key.size and bytes_used != len(buf):
            buf = self.read(key, start=buf_idx)
            bytes_used = trace.write(buf)
            buf_idx += len(buf)
        # XXX It is kind of silly. We unserialize the JSON-encoded string
        #     *data* for the response to JSON-encode it again. I haven't
        #     found out how to avoid this (see: rest_framework/response.py:37)
        data = str(trace)
        return json.loads(data)

