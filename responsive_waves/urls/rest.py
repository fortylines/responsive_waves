# Copyright (c) 2014, Fortylines LLC
# All rights reserved.

"""
urls for the REST API of fortylines waveform django app.
"""

from django.conf.urls import patterns, include, url
from responsive_waves.rest import (
    table_of_content, time_records, list_variables, update_variable,
    update_ranks)

urlpatterns = patterns('',
    url(r'^scope/(?P<waveform_id>\S+)/$',
        table_of_content, name='responsive_waves_scope'),
    url(r'^variables/(?P<waveform_id>\S+)/$',
        list_variables, name='responsive_waves_list_variables'),
    url(r'^values/(?P<waveform_id>\S+)/$',
        time_records, name='responsive_waves_time_records'),

    url(r'^browser/(?P<browser_id>\S+)/ranks',
        update_ranks, name='responsive_waves_update_ranks'),
    url(r'^browser/(?P<browser_id>\S+)/variables/(?P<pk>\S+)',
        update_variable, name='responsive_waves_update_variable'),
   )


