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

""" This module supplies the data model for the wave browser interface,
    well really, it just gives convenience routines for view.py """

import logging

from django.db import models

LOGGER = logging.getLogger(__name__)

VALID_SHAPES = ['bin', 'oct', 'dec', 'hex',
                'inv-bin', 'inv-oct', 'inv-dec', 'inv-hex',
                'bin-rev', 'oct-rev', 'dec-rev', 'hex-rev',
                'analog', 'gradient']

class Variable(models.Model):
    """
    Display option for a variable.
    """

    path = models.CharField(max_length=255)
    shown = models.BooleanField(default=False)
    is_leaf = models.BooleanField(default=True)
    browser = models.ForeignKey('Browser')
    # Order in the browser view (from top to bottom)
    rank = models.IntegerField(default=0)
    # Blob of text added to the style attribute of a DOM Node
    # DO NOT set default to {} otherwise UpdateVariableView with no 'style'
    # in request.DATA will reset the style to default.
    style = models.TextField(default="")
    # Display of the variable as Dec, Hex, etc.
    shape = models.SlugField(default="", blank=True)

    def __unicode__(self):
        return self.path


class Browser(models.Model):
    """
    A set of variables displayed together.
    """

    slug = models.SlugField()

    def __unicode__(self):
        return self.slug

