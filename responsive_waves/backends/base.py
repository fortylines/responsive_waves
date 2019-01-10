# Copyright (c) 2019, Sebastien Mirolo
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

import logging, subprocess

from responsive_waves import settings

LOGGER = logging.getLogger(__name__)


class _TraceProc(object):

    def __init__(self, proc):
        self.proc = proc
        self.out_text = ""
        self.err_text = ""

    def __str__(self):
        self.proc.stdin.close()
        output_text = self.proc.stdout.read()
        return output_text.decode('utf-8')

    def write(self, buf):
        bytes_used = self.proc.stdin.write(buf)
        return bytes_used


class BaseTraceBackend(object):

    @staticmethod
    def get_trace(variables, start_time, end_time, resolution):
        #pylint: disable=no-member
        cmdline = [settings.VCD2JSON_BIN,
            '-s', str(start_time), '-e', str(end_time), '-r', str(resolution)]
        for var in variables:
            cmdline += ['-n', var]
        return _TraceProc(subprocess.Popen(cmdline, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE))
