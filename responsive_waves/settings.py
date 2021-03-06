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

"""
Convenience module for access the waveform application settings. Default
settings are inforced when the main settings module does not contain
appropriate definitions.
"""
import os

from django.conf import settings


_SETTINGS = {
    'ACCOUNT_MODEL': settings.AUTH_USER_MODEL,
    'FILESYS_STORAGE': os.path.join(settings.BASE_DIR, 'build'),
    'FIXTURE_DIRS': [],
    'S3_STORAGE': None,
    'USE_FIXTURES': False,
    'VCD2JSON_BIN': getattr(settings, 'VCD2JSON_BIN', 'vcd2json'),
    'WAVEFORM_BACKENDS': ('responsive_waves.backends.filesys.VCDFileBackend',),
}
_SETTINGS.update(getattr(settings, 'RESPONSIVE_WAVES', {}))

ACCOUNT_MODEL = _SETTINGS.get('ACCOUNT_MODEL')
FIXTURE_DIRS = _SETTINGS.get('FIXTURE_DIRS')
FILESYS_STORAGE = _SETTINGS.get('FILESYS_STORAGE')
S3_STORAGE = _SETTINGS.get('S3_STORAGE')
USE_FIXTURES = _SETTINGS.get('USE_FIXTURES')
VCD2JSON_BIN = _SETTINGS.get('VCD2JSON_BIN')
WAVEFORM_BACKENDS = _SETTINGS.get('WAVEFORM_BACKENDS')
