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

'''Dynamic pages for browsing VCD files.'''

import json, logging, os, re

from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect, render_to_response
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import Http404
from django import forms
from django.views.generic import DetailView

from responsive_waves.models import Variable, Browser
from responsive_waves.utils import (variables_match, variables_root_prefixes,
                            variables_at_scope)
from responsive_waves.api import browser_from_path
from responsive_waves.backends import load_variables

LOGGER = logging.getLogger(__name__)


class BrowseView(DetailView):
    '''
    Returns an HTML5 page that contains the Value-Change-Over-Time
    browser javascript app.
    '''
    model = Browser
    slug_url_kwarg = 'waveform'
    template_name = 'responsive_waves/browse.html'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # Implementation Note:
            # Despite being a bad pattern, we create a ``Browser`` record
            # on a GET request here. There does not seem a more natural
            # place to do it if we want to avoid creating unnecessary browsers
            # for simulations which do not complete.
            self.object = Browser.objects.create(
                slug=self.kwargs[self.slug_url_kwarg])
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(BrowseView, self).get_context_data(**kwargs)
        browser = self.object
        title = browser.slug
        variables = Variable.objects.filter(
            browser=browser, shown=True).order_by('rank')
        serialized_list = []
        for entry in variables:
            fields = {}
            try:
                fields['style'] = json.loads(entry.style)
            except ValueError:
                fields['style'] = {}
            # If the shape of the waveform is not preset, we will defaults to
            # "analog" for single bit variables and "hex" for multi-bit
            # variables.
            if entry.shape:
                fields['shape'] = entry.shape
            elif re.match(r'\S+\[\d+:\d+\]', entry.path):
                fields['shape'] = 'hex'
            else:
                fields['shape'] = 'analog'
            fields['path'] = entry.path
            fields['id'] = str(entry.pk)
            serialized_list += [fields]
        context.update({
            'browser_path': browser.slug,
            # This JSON-serialization is a little complicated because we want
            # a subset of the fields to be encoded together with id but without
            # the additional model layers.
            'variable_list': json.dumps(serialized_list),
            'title': title,
            'waveform_id': self.kwargs[self.slug_url_kwarg],
            })
        context.update(csrf(self.request))
        return context


#pylint: disable=too-many-arguments,dangerous-default-value
def variable_list_app(request, browser, wave_path, fullpath_variable_list,
                      prefix=None, query=None,
                      write_permission=True, pathname=None):
    '''
    Index page for a variable or module. It displays a list of variables
    and modules rooted at *var_path*.
    '''
    try:
        variables = []
        for var_display in fullpath_variable_list:
            try:
                variables += [Variable.objects.get(
                        browser=browser, path=var_display.path)]
            except Variable.DoesNotExist:
                variables += [var_display]
        if not pathname:
            if browser:
                pathname = os.path.join(str(browser.id), wave_path)
            else:
                pathname = wave_path
        context = {
            'write_permission': write_permission,
            'browser_path': pathname,
            'root_path': prefix,
            'variable_list': variables
            }
        context.update(csrf(request))
        if query:
            context.update({'query': query})
        if prefix:
            context.update({'root_prefixes': variables_root_prefixes(prefix)})
        return render_to_response(
            "responsive_waves/waveform_variable_list.html", context)
    except KeyError:
        raise Http404


def variable_search_app(request, browser, wave_path,
                        variable_dict={}, write_permission=True,
                        pathname=None):
    '''
    Search for variables matching a regular expression
    '''
    query = request.GET.get('q', None)
    results = None
    if query:
        results = variables_match(query, variable_dict)
    return variable_list_app(request, browser, wave_path, results,
                             query=query,
                             write_permission=write_permission,
                             pathname=pathname)


class VariableToggleForm(forms.Form):
    path = forms.CharField(max_length=255)


def variable_toggle_app(request, browser, wave_path, variable_dict={},
                        write_permission=True,#pylint: disable=unused-argument
                        pathname=None):
    '''
    Add a variable *var_path* to the waveform browser for *slug*.
    '''
    if request.method == 'POST':
        form = VariableToggleForm(request.POST)
        if form.is_valid():
            for var_matched in variables_match(form.cleaned_data['var_path'],
                                               variable_dict):
                if var_matched.is_leaf:
                    var_options, _ = Variable.objects.get_or_create(
                        browser=browser, path=var_matched.path)
                    var_options.shown = not var_options.shown
                    var_options.save()
    if not pathname:
        if browser:
            pathname = os.path.join(str(browser.id, wave_path))
        else:
            pathname = wave_path
    return redirect(request.META.get('HTTP_REFERER',
                       reverse('responsive_waves_variable_list',
                               args=(pathname, ''))))



@require_GET
def variable_list(request, pathname, var_path):
    '''
    Index page for a variable or module. It displays a list of variables
    and modules rooted at *var_path*.
    '''
    browser, wave_path = browser_from_path(pathname)
    return variable_list_app(request, browser, wave_path,
        variables_at_scope(load_variables(wave_path), prefix=var_path),
        prefix=var_path)


@require_GET
def variable_search(request, pathname):
    browser, wave_path = browser_from_path(pathname)
    return variable_search_app(request, browser, wave_path,
                               variable_dict=load_variables(wave_path))


@require_POST
def variable_toggle(request, pathname,
                    variables_scope={}): #pylint: disable=unused-argument
    '''
    Add a variable *var_path* to the waveform browser for *slug*.
    '''
    browser, wave_path = browser_from_path(pathname)
    return variable_toggle_app(request, browser, wave_path,
                               variable_dict=load_variables(wave_path))

