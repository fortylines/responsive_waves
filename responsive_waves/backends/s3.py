# Copyright (c) 2017, Sebastien Mirolo
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

import json, logging

import boto
from boto.exception import S3ResponseError
from django.http import Http404

from responsive_waves import settings
from responsive_waves.backends.base import BaseTraceBackend


LOGGER = logging.getLogger(__name__)
BUFFER_SIZE = 4096


class VCDS3Backend(BaseTraceBackend):

    @property
    def bucket(self):
        # We lazily initialize ``bucket`` instead of doing it
        # in the constructor to avoid raising exceptions just
        # on a ``load_backend``.
        if not hasattr(self, "_bucket"):
            if settings.S3_STORAGE is None:
                raise IOError("S3_STORAGE should not be None (ex: s3://bucket)")
            conn = boto.connect_s3()
            remote_location = settings.S3_STORAGE
            try:
                self._bucket = conn.get_bucket(remote_location[5:])
            except S3ResponseError as err:
                raise Http404(err)
        return self._bucket

    def get_key(self, key_name):
        key = self.bucket.get_key(key_name)
        if key is None:
            LOGGER.warning("'%s' not found", key_name)
            raise KeyError(key)
        return key

    @staticmethod
    def read(key, start=0):
        LOGGER.debug("GET [%d, %d] from key %s in S3 bucket %s",
            start, start + BUFFER_SIZE, key.name, key.bucket)
        return key.get_contents_as_string(
            headers={'Content-Range':
                'bytes %d-%d/*' % (start, start + BUFFER_SIZE)})

    def load_variables(self, vcd_path):
        """
        Returns a scope tree (as a python dictionnary) of variables defined
        in *vcd_path*.
        """
        if not vcd_path.endswith('.vcd'):
            vcd_path += '.vcd'
        trace = self.get_trace([], 0, 0, 1)
        LOGGER.debug('GET %s in bucket %s', vcd_path, self.bucket)
        key = self.get_key(vcd_path)
        bytes_used = 1
        buf_idx = 0
        buf = []
        while buf_idx < key.size and bytes_used != len(buf):
            buf = self.read(key, start=buf_idx)
            bytes_used = trace.write(buf)
            buf_idx += len(buf)
        data = str(trace)
        return json.loads(data)['definitions']

    def load_values(self, vcd_path,
                    variables, start_time, end_time, resolution):
        #pylint: disable=too-many-arguments
        '''
        Returns a json-formatted version of the time records
        for the VCD file pointed by *job_id*/*vcd_path*.
        '''
        if not vcd_path.endswith('.vcd'):
            vcd_path += '.vcd'
        LOGGER.debug("[load_values] %s %s [%ld, %ld[ at %d",
                     vcd_path, variables, start_time, end_time, resolution)
        trace = self.get_trace(variables, start_time, end_time, resolution)
        key = self.get_key(vcd_path)
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

    def retrieve(self, key_name):
        """
        Return content of a log file (stdout, stderr, etc.)
        """
        key = self.get_key(key_name)
        return key.get_contents_as_string()
