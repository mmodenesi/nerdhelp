# -*- coding: utf-8 -*-
"""
Prueba
"""

from django.core.management.base import BaseCommand

from definitions.models import Concept
from definitions.utils import concepts2latex
from definitions.utils import latex2pdf

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        c = Concept.objects.all()[:2]
        latex = concepts2latex(c)
        path = '/tmp/nerdhelp.pdf'
        latex2pdf(latex, path)

