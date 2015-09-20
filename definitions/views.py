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
from django_ajax.decorators import ajax

# project imports
from definitions.models import Concept
from definitions.models import Course

SUGGESTED_CARDS = 7

def search(request):
    """Show search results"""

    query = request.GET.get('q', None)
    if query:
        query = query.strip()

    result = []
    for token in query.split():
        result.extend(Concept.objects.filter(name__icontains=token))
        result.extend(Concept.objects.filter(definition__icontains=token))
        result.extend(Concept.objects.filter(tags__name__icontains=token))

    result = set(result)

    context = {
        'courses': Course.objects.all().order_by('name'),
        'query': query,
        'result': result,
    }
    return render(request, 'definitions/search_results.html', context)


def add_card(request):
    """Add a new concept"""
    context = {
        'courses': Course.objects.all().order_by('name'),
        'concept_types': Concept.TYPE_OF_CARD,
    }
    return render(request, 'definitions/edit_card.html', context)

def view_card(request, card_id):
    """Show specific card"""

    card = get_object_or_404(Concept, pk=card_id)

    context = {
        'progress': card.course.progress(),
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
        concepts = Concept.objects.filter(course__id=int(course_id)).order_by('learning_coeff')
    else:
        concepts = Concept.objects.all().order_by('learning_coeff')


    concepts = concepts[:max(len(concepts)/10, 6)]

    card = random.choice(concepts)

    return redirect('view_card', card.id)

def rank_up(_, concept_id):
    """
    Rank up this concept
    """
    concept = Concept.objects.get(id=concept_id)
    concept.learning_coeff += 1
    concept.learning_coeff = min(concept.learning_coeff, 10.0)
    concept.save()
    return HttpResponse(json.dumps(dict(result='ok')),
                        content_type="application/json")

def rank_down(_, concept_id):
    """
    Rank down this concept
    """
    concept = Concept.objects.get(id=concept_id)
    concept.learning_coeff -= 1.5
    concept.learning_coeff = max(concept.learning_coeff, 0.0)
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

