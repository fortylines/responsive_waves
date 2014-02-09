# Copyright (c) 2014, Fortylines LLC
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

import json, logging, re, time
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView

from responsive_waves.models import (VALID_SHAPES, Browser, Variable)
from responsive_waves.backends import load_variables, load_values
from responsive_waves.utils import NODE_SEP, variables_match

LOGGER = logging.getLogger(__name__)

def browser_from_path(url_path):
    paths = url_path.split('/')
    browser_id = paths[0]
    try:
        browser = Browser.objects.get(pk=browser_id)
        wave_path = '/'.join(paths[1:])
    except (Browser.DoesNotExist, ValueError):
        # It might not be possible to convert the browser_id to an int.
        browser = None
        wave_path = url_path
    return browser, wave_path


class VariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = ('style', 'shape')


class UpdateVariableView(UpdateAPIView):
    """
    Updating a Variable Display

    Updates the specified variable by setting the values of the parameters
    passed. Any parameters not provided will be left unchanged. For example,
    if you pass the color parameter, that becomes the variable's color to be
    used for display in a wave browser.

    This request accepts the same arguments as the variable creation call.
    """

    model = Variable
    serializer_class = VariableSerializer
    slug_url_kwarg = 'path'
    slug_field = 'path'

    def update(self, request, *args, **kwargs):
        LOGGER.debug('update args=%s, kwargs=%s, DATA=%s',
                     args, kwargs, request.DATA)
        if 'style' in request.DATA:
            request.DATA['style'] = json.dumps(request.DATA['style'])
        if 'shape' in request.DATA:
            if not request.DATA['shape'] in VALID_SHAPES:
                request.DATA.pop('shape')
        return super(UpdateVariableView, self).update(request, *args, **kwargs)


@api_view(['GET'])
def table_of_content(request, wave_path):
    '''
    Table of content for a value change (wave) file.
    '''
    if request.method == 'GET':
        data = load_variables(wave_path)
        # XXX It is kind of silly. We unserialize the JSON-encoded string
        #     *data* for the response to JSON-encode it again. I haven't
        #     found out how to avoid this (see: rest_framework/response.py:37)
        return Response(data)


def _as_validated_long(request, name, default):
    try:
        return long(request.REQUEST.get(name, default))
    except ValueError:
        return default


def query_db_variables(variables):
    query_names = {}
    for entry in Variable.objects.filter(
        pk__in=variables).values('pk', 'path'):
        query_names[entry['path']] = entry['pk']
    return query_names


@api_view(['GET'])
def time_records(request, waveform_id):
    """
    Returns a list of values for a set of variables defined in an waveform.

    DEFINITION
    GET https://api.fortylines.com/v1/values/{WAVEFORM_ID}

    EXAMPLE PARAMETERS
    { "vars": [ "board.clock" ],
      "start_time": 0,
      "end_time": 1000,
      "res": 0
    }

    EXAMPLE RESPONSE
    { [
        { "path", "",
          "values: [ [0, 1], [100, 0], [200, 1] ]
        },
        ...
    ] }
    """
    query_names = {}
    variables = json.loads(request.REQUEST.get('vars', "[]"))
    if not isinstance(variables, list):
        raise ValueError
    start_time = _as_validated_long(request, 'start_time', 0)
    end_time = _as_validated_long(request, 'end_time', 1000)
    resolution = _as_validated_long(request, 'res', 1)
    return Response(load_values(waveform_id, variables,
                                start_time, end_time, resolution))


@api_view(['PUT'])
def update_ranks(request, pathname):
    '''DATA is a list of variable ids. The ordering indicates the new ranks.'''
    LOGGER.debug('[update_ranks] request.DATA: %s', request.DATA)
    browser, wave_path = browser_from_path(pathname)
    if browser:
        # XXX If we don't have a browser here, there is nothing to update
        # in the database.
        variable_list = Variable.objects.filter(
            browser=browser, shown=True).order_by('rank')
        for rank, path in enumerate(request.DATA):
            this_variable = Variable.objects.get_or_create(
                path=path, browser=browser, shown=True)
            LOGGER.info(
                "[update_ranks] %s from %d to %d",
                this_variable.id, this_variable.rank, rank)
            this_variable.rank = rank
            this_variable.save()
            variable_list = variable_list.exclude(path=path)
        if len(variable_list) > 0:
            # XXX This is not a full ordering, abort
            raise ValueError
    return Response("OK")


@api_view(['PUT'])
def update_variable(request, pathname, pk):
    '''Update the display state associated to a variable.'''
    view = UpdateVariableView.as_view()
    return view(request, path=pk)


@api_view(['GET'])
def list_variables(request, waveform_id):
    """
    Returns the list of variables defined in an waveform.

    DEFINITION
    GET https://api.fortylines.com/v1/variables/{WAVEFORM_ID}

    EXAMPLE RESPONSE
    { [
        { "path", "",
          "is_leaf: true,
          "shown": true,
          "rank": 0,
          "style": "",
          "shape": "analog"
        },
        ...
    ] }
    """
    top_scope = load_variables(waveform_id)
    # *load_variables* returns a scope tree implemented as a dictionnary
    # of <string: dict> and <string: string>.
    # Each <string: dict> is a scoped module which associates the name
    # of the module to the variables defined in that module. The definition
    # is recusive.

    query = request.GET.get('q', None)
    if not query:
        # No query, we return no results.
        query = r'^$'
        if False:
            # Return variables defined at the toplevel when no scope is specified.
            query = (r'^[^%(node_sep)s]+%(node_sep)s[^%(node_sep)s]+%(node_sep)s?$'
                     % {'node_sep': NODE_SEP})
    if query.startswith(NODE_SEP):
        query = query[1:]
    query_variables = variables_match(query, top_scope)

    # *variables_match* returns a list of Variable object whose full path
    # from the root matches the *query* regular expression.

    browser, _ = browser_from_path(waveform_id)
    if browser:
        decorated_variables = []
        for variable in query_variables:
            try:
                variable = Variable.objects.get(
                    path=variable.path, browser=browser)
            except Variable.DoesNotExist:
                pass
            decorated_variables += [ variable ]
    else:
        decorated_variables = query_variables
    # This list of variables is decorated with the persistant state at this
    # point. It is time to return it as a json blob.

    serialized_variables = []
    for variable in decorated_variables:
        fields = {
            'path': variable.path,
            'is_leaf': variable.is_leaf,
            'shown': variable.shown,
            'rank':  variable.rank
            }
        try:
            fields['style'] = json.loads(variable.style)
        except ValueError:
            fields['style'] = {}
        # If the shape of the waveform is not preset, we will defaults to
        # "analog" for single bit variables and "hex" for multi-bit variables.
        if variable.shape:
            fields['shape'] = variable.shape
        elif re.match(r'\S+\[\d+:\d+\]', variable.path):
            fields['shape'] = 'hex'
        else:
            fields['shape'] = 'analog'
        serialized_variables += [ fields ]
    return Response(serialized_variables)
