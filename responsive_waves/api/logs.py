# Copyright (c) 2019, Sebastien Mirolo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging, re, os

from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView
from responsive_waves import backends


LOGGER = logging.getLogger(__name__)


class RetrieveLogAPIView(RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        resp = {}
        log_key = self.kwargs.get('key')
        sep = log_key.find('/')
        job_id = log_key[:sep] if sep else None
        log_content = backends.retrieve_key(log_key)
        if log_content and log_key.endswith(".simwrap"):
            for output in log_content.splitlines():
                if re.match(r".*\.vcd", output):
                    if job_id:
                        browser_path = os.path.join(
                            job_id, os.path.splitext(output)[0])
                    else:
                        browser_path = os.path.splitext(output)[0]
                    waveform_url = browser_path
                    resp.update({'waveform': (waveform_url, output)})
        else:
            resp = {log_key: log_content}
        return Response(resp)


class LogListAPIView(ListAPIView):

    pass
