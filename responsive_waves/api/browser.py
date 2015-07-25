# Copyright (c) 2015, Sebastien Mirolo
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

import json, logging

from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, RetrieveUpdateAPIView

from responsive_waves.models import (VALID_SHAPES, Browser, Variable)


LOGGER = logging.getLogger(__name__)


class VariableSerializer(serializers.ModelSerializer):
    #pylint: disable=no-init,old-style-class

    shape = serializers.SlugField(required=False)

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


class RankAPIView(RetrieveUpdateAPIView):
    """
    Update the variables displayed in a waveform browser.

    DEFINITION
    PUT https://api.fortylines.com/v1/browser/:browser/ranks

    EXAMPLE PARAMETERS
    [ "board.clock", "board.counter" ]

    EXAMPLE RESPONSE
    OK
    """

    model = Browser
    slug_url_kwarg = 'browser'

    @method_decorator(transaction.atomic)
    def put(self, request, *args, **kwargs):
        """
        DATA is a list of variable ids. The ordering indicates the new ranks.
        """
        LOGGER.debug('[update_ranks] request.DATA: %s', request.DATA)
        browser = self.get_object()
        # will throw a 404 if we cannot find a borwser to update.
        variable_list = Variable.objects.filter(
            browser=browser, shown=True).order_by('rank')
        for rank, path in enumerate(request.DATA):
            this_variable, _ = Variable.objects.get_or_create(
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
