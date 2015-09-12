# -*- coding: utf-8 -*-
# pylint: disable=old-style-class
"""
Forms to edit cards
"""

from django import forms
from definitions.models import Concept
from ckeditor.widgets import CKEditorWidget

class ConceptForm(forms.ModelForm):
    """Form to edit a concept or add a new concept"""
    title = forms.CharField(required=True)
    concept = forms.CharField(widget=CKEditorWidget())
    tags = forms.CharField(required=True)

    class Meta:
        """..."""
        model = Concept
        fields = '__all__'

