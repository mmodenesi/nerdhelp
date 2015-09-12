# -*- coding: utf-8 -*-
"""
Admin for app definitions
"""

from django.contrib import admin

from definitions.models import Concept
from definitions.models import Course
from definitions.models import Tag
from definitions.models import Reaction

class ConceptAdmin(admin.ModelAdmin):
    """ModelAdmin for Concept"""
    list_display = ('name', 'concept_type', 'learning_coeff')
    list_filter = ('concept_type', )
    fields = ['concept_type', 'course', 'name', 'definition']


class CourseAdmin(admin.ModelAdmin):
    """ModelAdmin for Course"""
    pass


class TagAdmin(admin.ModelAdmin):
    """ModelAdmin for Tag"""
    pass


admin.site.register(Concept, ConceptAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Tag, TagAdmin)




