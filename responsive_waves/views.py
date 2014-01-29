# Copyright (c) 2013, Fortylines LLC
#   All rights reserved.

'''Dynamic pages for browsing VCD files.'''

import json, logging, os, re

from django.views.generic.list import ListView
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect, render_to_response
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import Http404
from django import forms

from responsive_waves.models import Variable
from responsive_waves.utils import (variables_match, variables_root_prefixes,
                            variables_at_scope)
from responsive_waves.rest import browser_from_path
from responsive_waves.backends import load_variables

LOGGER = logging.getLogger(__name__)


def browse(request, waveform_id, title='', browser_path=None):
    '''
    Returns an HTML5 page that contains the Value-Change-Over-Time
    browser javascript app.
    '''
    browser, wave_path = browser_from_path(waveform_id)
    if not title:
        title = wave_path
    variable_list = Variable.objects.filter(
        browser=browser, shown=True).order_by('rank')
    serialized_list = []
    for entry in variable_list:
        fields = {}
        try:
            fields['style'] = json.loads(entry.style)
        except ValueError:
            fields['style'] = {}
        # If the shape of the waveform is not preset, we will defaults to
        # "analog" for single bit variables and "hex" for multi-bit variables.
        if entry.shape:
            fields['shape'] = entry.shape
        elif re.match(r'\S+\[\d+:\d+\]', entry.path):
            fields['shape'] = 'hex'
        else:
            fields['shape'] = 'analog'
        fields['path'] = entry.path
        fields['id'] = str(entry.pk)
        serialized_list += [ fields ]
    if not browser_path:
        browser_path = waveform_id
    context = {
        'browser_path': browser_path,
        # This JSON-serialization is a little complicated because we want
        # a subset of the fields to be encoded together with id but without
        # the additional model layers.
        'variable_list': json.dumps(serialized_list),
        'title': title,
        'waveform_id':  browser_path
        }
    context.update(csrf(request))
    return render_to_response("responsive_waves/browse.html", context)



def variable_list_app(request, browser, wave_path, fullpath_variable_list,
                      prefix=None, query=None,
                      write_permission=True, pathname=None):
    '''
    Index page for a variable or module. It displays a list of variables
    and modules rooted at *var_path*.
    '''
    try:
        variable_list = []
        for var_display in fullpath_variable_list:
            try:
                variable_list += [ Variable.objects.get(
                        browser=browser, path=var_display.path) ]
            except Variable.DoesNotExist:
                variable_list += [ var_display ]
        if not pathname:
            if browser:
                pathname = os.path.join(str(browser.id), wave_path)
            else:
                pathname = wave_path
        context = {
            'write_permission': write_permission,
            'browser_path': pathname,
            'root_path': prefix,
            'variable_list': variable_list
            }
        context.update(csrf(request))
        if query:
            context.update({ 'query': query })
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


def variable_toggle_app(request, browser, wave_path,
                        variable_dict={}, write_permission=True,
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
                               args=(pathname,''))))



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
                               variable_dict = load_variables(wave_path))


class VariableToggleForm(forms.Form):
    var_path = forms.CharField(max_length=255)


@require_POST
def variable_toggle(request, pathname, variables_scope={}):
    '''
    Add a variable *var_path* to the waveform browser for *slug*.
    '''
    browser, wave_path = browser_from_path(pathname)
    return variable_toggle_app(request, browser, wave_path,
                               variable_dict = load_variables(wave_path))

