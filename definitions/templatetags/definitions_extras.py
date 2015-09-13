# -*- coding: utf-8 -*-
"""
Template tags for app definitions
"""

from django import template

register = template.Library()

def truncate_math(value, n_chars):
    """Truncate chars, but don't in the middle of a formula!"""

    result = []
    dollar_signs = 0
    parentesis = 0
    index = 0
    while n_chars > index or dollar_signs % 2 == 1 or parentesis == 1:
        try:
            char = value[index]
        except IndexError:
            break

        print char
        if char == '$':
            dollar_signs += 1
        if char == '(':
            parentesis += 1
        if char == ')':
            parentesis -= 1
        index += 1
        result.append(char)
        print result
    return ''.join(result)


register.filter('truncate_math', truncate_math)

