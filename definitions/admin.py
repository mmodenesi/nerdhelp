# -*- coding: utf-8 -*-
"""
Admin for app definitions
"""

from django.contrib import admin

from definitions.models import Concept
from definitions.models import Course
from definitions.models import Tag

class ConceptAdmin(admin.ModelAdmin):
    """ModelAdmin for Concept"""
    list_display = ('name', 'concept_type', 'learning_coeff')
    list_filter = ('concept_type', 'course')
    fields = ['concept_type', 'course', 'name', 'definition', 'tags']


class CourseAdmin(admin.ModelAdmin):
    """ModelAdmin for Course"""
    pass


class TagAdmin(admin.ModelAdmin):
    """ModelAdmin for Tag"""
    pass


admin.site.register(Concept, ConceptAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Tag, TagAdmin)




