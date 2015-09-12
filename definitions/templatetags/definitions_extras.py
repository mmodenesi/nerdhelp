# -*- coding: utf-8 -*-
"""
Template tags for app definitions
"""

from django import template

register = template.Library()

def double_slashes(value):
    """Replace backslash with double backslash"""
    return value.replace('\\', '\\\\')

register.filter('double_slashes', double_slashes)

