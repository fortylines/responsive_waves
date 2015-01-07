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

"""
urls for the REST API of responsive_waves django app.
"""

from django.conf.urls import patterns, url
from responsive_waves.api import (
    table_of_content, time_records, list_variables, UpdateVariableView,
    RankAPIView)

urlpatterns = patterns('',
    url(r'^scope/(?P<waveform_id>\S+)/$',
        table_of_content, name='responsive_waves_scope'),
    url(r'^variables/(?P<waveform_id>\S+)/$',
        list_variables, name='responsive_waves_list_variables'),
    url(r'^values/(?P<waveform_id>\S+)/$',
        time_records, name='responsive_waves_time_records'),

    url(r'^browser/(?P<browser>\S+)/ranks',
        RankAPIView.as_view(), name='responsive_waves_update_ranks'),
    url(r'^browser/(?P<browser>\S+)/variables/(?P<path>\S+)?',
        UpdateVariableView.as_view(), name='responsive_waves_update_variable'),
   )


