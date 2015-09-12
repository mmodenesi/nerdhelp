# pylint: disable=multiple-statements, line-too-long
"""
Views for app definitions
"""
# python imports
import random
import json

# django imports
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from django_ajax.decorators import ajax

# project imports
from definitions.models import Concept
from definitions.models import Course

SUGGESTED_CARDS = 5


def add_card(request):
    """Add a new concept"""
    context = {
        'courses': Course.objects.all().order_by('name'),
        'concept_types': Concept.TYPE_OF_CARD,
        'ckeditor_config': json.dumps(settings.CKEDITOR_CONFIGS['default']),
    }
    return render(request, 'definitions/edit_card.html', context)

def view_card(request, card_id):
    """Show specific card"""
    card = get_object_or_404(Concept, pk=card_id)
    context = {
        'card': card,
        'suggested_cards': Concept.objects.filter(course=card.course).exclude(
            id=card.id).order_by('learning_coeff')[:SUGGESTED_CARDS],
        'courses': Course.objects.all().exclude(id=card.course.id),
    }

    return render(request, 'definitions/learn.html', context)

def edit_card(request, card_id):
    """Edit card"""
    card = get_object_or_404(Concept, pk=card_id)
    context = {
        'card': card,
        'courses': Course.objects.all(),
        'concept_types': Concept.TYPE_OF_CARD,
        'ckeditor_config': json.dumps(settings.CKEDITOR_CONFIGS['default']),
    }
    return render(request, 'definitions/edit_card.html', context)

@ajax
def save_card(request):
    """Save card changes to database or add new card"""
    if request.POST:
        card_id = request.POST.get('card_id', None)
        course_name = request.POST.get('course_name')
        concept_type = request.POST.get('concept_type')
        title = request.POST.get('title')
        definition = request.POST.get('definition')
        course, _ = Course.objects.get_or_create(name=course_name.strip())
        if card_id:
            card = get_object_or_404(Concept, pk=int(card_id))
            card.name = title
            card.definition = definition
            card.course = course
            card.concept_type = concept_type
        else:
            card = Concept.objects.create(
                name=title,
                definition=definition,
                course=course,
                concept_type=concept_type
            )

        card.save()
        return {"status": 200, "statusText": "OK", 'card_id': card.id}

def random_card(request):
    """Show random concept"""

    course_id = request.GET.get('c', None)
    if course_id:
        concepts = Concept.objects.filter(course__id=int(course_id))
    else:
        concepts = Concept.objects.all()

    try:
        card = random.choice(concepts[1:])
    except IndexError:
        # there's only one card
        card = concepts[0]

    return redirect('view_card', card.id)

def rank_up(_, concept_id):
    """
    Rank up this concept
    """
    concept = Concept.objects.get(id=concept_id)
    concept.learning_coeff += 1
    concept.save()
    return HttpResponse(json.dumps(dict(result='ok')),
                        content_type="application/json")

def rank_down(_, concept_id):
    """
    Rank down this concept
    """
    concept = Concept.objects.get(id=concept_id)
    concept.learning_coeff -= 1.5
    concept.save()
    return HttpResponse(json.dumps(dict(result='ok')),
                        content_type="application/json")

def home(request):
    """
    home
    """
    context = {
        'suggested_cards': Concept.objects.all().order_by('learning_coeff')[:SUGGESTED_CARDS],
    }
    return render(request, 'definitions/home.html', context)

