# Copyright (c) 2014, Fortylines LLC
#   All rights reserved.

""" This module supplies the data model for the wave browser interface,
    well really, it just gives convenience routines for view.py """

import logging

from django.db import models

LOGGER = logging.getLogger(__name__)

VALID_SHAPES = [ 'bin', 'oct', 'dec', 'hex',
                 'inv-bin', 'inv-oct', 'inv-dec', 'inv-hex',
                 'bin-rev', 'oct-rev', 'dec-rev', 'hex-rev',
                 'analog', 'gradient' ]

class Variable(models.Model):
    '''Display option for a variable.'''
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
    shape = models.SlugField(default="")


class Browser(models.Model):
    '''A set of variables displayed together.'''
    slug = models.SlugField()


