# -*- coding: utf-8 -*-
"""
Models for app definitions
"""

from django.db import models

DESIRED_LEARNING_COEFF = 10.0


class Course(models.Model):
    """
    Course where you learn a Concept
    """
    name = models.CharField(max_length=100)

    def progress(self):
        """Return estimative progress with this course cards"""

        # get all cards
        cards = Concept.objects.filter(course=self)
        percentages = sum([c.progress() for c in cards])
        return percentages / len(cards)

    def __unicode__(self):
        """..."""
        return self.name


class Tag(models.Model):
    """
    Tags
    """
    name = models.CharField(max_length=80)


    def __unicode__(self):
        return self.name


class Concept(models.Model):
    """
    Something to learn
    """

    THEOREM = 'T'
    LEMA = 'L'
    DEFINITION = 'D'
    EXAMPLE = 'E'
    PROBLEM = 'P'
    COROLLARY = 'C'


    TYPE_OF_CARD = (
        (THEOREM, 'Teorema'),
        (LEMA, 'Lema'),
        (DEFINITION, u'Definición'),
        (EXAMPLE, 'Ejemplo'),
        (PROBLEM, 'Problema'),
        (COROLLARY, 'Corolario'),
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
        result = result.replace('\\', '\\\\')
        result = result.replace('"', r'\"')
        result = r'\n'.join(result.split('\n'))
        return result

    def progress(self):
        """Return progress in learning this card"""
        perc = self.learning_coeff / DESIRED_LEARNING_COEFF * 100
        return max(min(perc, 100.0), 0.0)


class Reaction(models.Model):
    """
    User's answer to the apparition of a card
    """
    card = models.ForeignKey(Concept, related_name='reactions')
    value = models.IntegerField()
    created = models.DateTimeField(editable=False, auto_now_add=True)


class Filter(models.Model):
    """
    Filters
    """
    visible_name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
