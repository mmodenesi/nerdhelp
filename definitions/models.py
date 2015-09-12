# -*- coding: utf-8 -*-
"""
Models for app definitions
"""

from django.db import models


class Course(models.Model):
    """
    Course where you learn a Concept
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        """..."""
        return self.name


class Tag(models.Model):
    """
    Tags
    """
    name = models.CharField(max_length=80)


class Concept(models.Model):
    """
    Something to learn
    """

    THEOREM = 'T'
    LEMA = 'L'
    DEFINITION = 'D'
    EXAMPLE = 'E'
    PROBLEM = 'P'


    TYPE_OF_CARD = (
        (THEOREM, 'Teorema'),
        (LEMA, 'Lema'),
        (DEFINITION, 'Definición'),
        (EXAMPLE, 'Ejemplo'),
        (PROBLEM, 'Problema'),
    )

    name = models.CharField(max_length=500)
    definition = models.TextField()
    course = models.ForeignKey(Course)
    tags = models.ManyToManyField(Tag)
    learning_coeff = models.FloatField(editable=False, default=0.0)
    concept_type = models.CharField(max_length=1,
                                    choices=TYPE_OF_CARD,
                                    default=DEFINITION)

    def update_learning_coeff(self):
        """Update the value of the learning coefficient
        (presumably, there are new inputs from the user)
        """
        pass

    def __unicode__(self):
        """..."""
        return self.name

    def clean_definition(self):
        """Return string prepared to be inserted in javascript"""
        result = self.definition.replace('\r\n', '\n')
        result = ' '.join(result.split('\n'))
        result = result.replace('\\', '\\\\')
        result = result.replace('"', r'\"')
        return result


class Reaction(models.Model):
    """
    User's answer to the apparition of a card
    """
    card = models.ForeignKey(Concept, related_name='reactions')
    value = models.IntegerField()
    created = models.DateTimeField(editable=False, auto_now_add=True)

