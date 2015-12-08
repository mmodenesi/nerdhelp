# pylint: disable=multiple-statements, line-too-long
"""
Views for app definitions
"""
# python imports
import random
import operator
import json

# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django_ajax.decorators import ajax
from django.views.decorators.csrf import csrf_exempt

# project imports
from definitions.models import Concept
from definitions.models import Course
from definitions.models import Tag
from definitions.models import Filter


COURSE = 'C'
TYPE = 'T'
TAG = 'E'

def prev_card(_, card_id):
    """Show prev card, according to current filters"""
    concepts = get_concepts_applying_filters().order_by('-pk')
    if concepts.filter(id__lt=card_id):
        card = concepts.filter(id__lt=card_id)[0]
    else:
        card = concepts[0]
    return redirect('view_card', card.id)

def next_card(_, card_id):
    """Show next card, according to current filters"""
    concepts = get_concepts_applying_filters().order_by('pk')
    if concepts.filter(id__gt=card_id):
        card = concepts.filter(id__gt=card_id)[0]
    else:
        card = concepts[0]
    return redirect('view_card', card.id)

def get_tags(_):
    """return json with tagnames"""
    return HttpResponse(json.dumps(sorted([t.name for t in Tag.objects.all()])),
                        content_type="application/json")

@csrf_exempt
@ajax
def set_filter(request):
    """Activate or deativate Filter"""
    if request.POST:
        name = request.POST['name']
        value = request.POST['value']
        state = bool(int(request.POST['state']))
        f, _ = Filter.objects.get_or_create(visible_name=name, value=value)
        f.active = state
        f.save()

@csrf_exempt
def autocomplete(request):
    """return possible filters"""
    response_data = []
    if request.POST:
        query = request.POST.get('query', None)
        if query:
            query = query.lower().strip()

            # filtros por Course
            matches = Course.objects.filter(name__icontains=query)
            for m in matches:
                value = '%s;%s' % (COURSE, m.id)
                if not Filter.objects.filter(active=True, value=value):
                    response_data.append(
                        dict(id=value,
                             name=m.__unicode__(),
                             tipo='Curso')
                        )

            # filtros por Tag
            matches = Tag.objects.filter(name__icontains=query)
            for m in matches:
                value = '%s;%s' % (TAG, m.id)
                if not Filter.objects.filter(active=True, value=value):
                    response_data.append(
                        dict(id=value,
                             name=m.__unicode__(),
                             tipo='Etiqueta')
                        )


            # filtros por Concept.type
            for value, name in Concept.TYPE_OF_CARD:
                if query in name.lower():
                    value = '%s;%s' % (TYPE, value)
                    if not Filter.objects.filter(active=True, value=value):
                        response_data.append(
                            dict(id=value,
                                 name=name,
                                 tipo='Tipo de concepto')
                            )

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


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
    else:
        result = get_concepts_applying_filters().order_by('course__id', 'pk')

    context = {
        'courses': Course.objects.all().order_by('name'),
        'query': query,
        'result': result,
        'filters': [{'visible_name': f.visible_name, 'value': f.value}
                    for f in Filter.objects.filter(active=True)],
    }
    return render(request, 'definitions/search_results.html', context)


def add_card(request):
    """Add a new concept"""
    if request.GET:
        # just a hack to make the template pre-select correct
        # course for you
        card = {}
        try:
            card['course'] = Course.objects.get(id=request.GET['c'])
        except ObjectDoesNotExist:
            card = None
    else:
        card = None
    context = {
        'card': card,
        'courses': Course.objects.all().order_by('name'),
        'concept_types': Concept.TYPE_OF_CARD,
        'tags': Tag.objects.all(),
    }
    return render(request, 'definitions/edit_card.html', context)

def view_card(request, card_id):
    """Show specific card"""

    card = get_object_or_404(Concept, pk=card_id)

    filtered = get_concepts_applying_filters()
    if filtered:
        progress = sum([c.progress() for c in filtered]) / len(filtered)
    else:
        progress = card.course.progress()

    context = {
        'progress': progress,
        'card': card,
        'courses': Course.objects.all().exclude(id=card.course.id),
        'filters': [{'visible_name': f.visible_name, 'value': f.value}
                    for f in Filter.objects.filter(active=True)],
    }

    return render(request, 'definitions/learn.html', context)

def edit_card(request, card_id):
    """Edit card"""
    card = get_object_or_404(Concept, pk=card_id)
    context = {
        'card': card,
        'courses': Course.objects.all().order_by('name'),
        'concept_types': Concept.TYPE_OF_CARD,
        'tags': Tag.objects.all(),
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
        tags_strings = request.POST.get('tags', '')
        if tags_strings:
            tags_list = tags_strings.split(',')
        else:
            tags_list = []
        tags_instances = [Tag.objects.get_or_create(name=name)[0] for name in tags_list]

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
        for t in tags_instances:
            card.tags.add(t)
        for t in card.tags.all():
            if not t in tags_instances:
                card.tags.remove(t)

        return {"status": 200, "statusText": "OK", 'card_id': card.id}

def get_concepts_applying_filters():
    """Apply active filters to show significative concepts"""
    active_filters = Filter.objects.filter(active=True)
    if active_filters:
        qs_courses = [Q()]
        qs_tags = [Q()]
        qs_types = [Q()]
        for f in active_filters:
            key, value = f.value.split(';')
            if key == 'E':
                qs_tags.append(Q(tags__id=value))
            elif key == 'C':
                qs_courses.append(Q(course__id=value))
            elif key == 'T':
                qs_types.append(Q(concept_type=value))
        q_courses = reduce(operator.or_, qs_courses)
        q_tags = reduce(operator.or_, qs_tags)
        q_types = reduce(operator.or_, qs_types)
        q = Q(q_courses & q_tags & q_types)
        concepts = Concept.objects.filter(q)
    else:
        concepts = Concept.objects.all()
    return concepts.distinct().order_by('id')

def random_card(_):
    """Show random concept"""
    concepts = get_concepts_applying_filters()
    concepts = concepts.order_by('learning_coeff')
    if len(concepts) > 20:
        concepts = concepts[:20]
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
        'courses': Course.objects.all().order_by('name'),
        'filters': [{'visible_name': f.visible_name, 'value': f.value}
                    for f in Filter.objects.filter(active=True)],
    }
    return render(request, 'definitions/home.html', context)


def view_course(request, course_id):
    """
    Show details for this course
    """
    course = get_object_or_404(Course, pk=course_id)
    context = {
        'course': course,
        'concepts': Concept.objects.filter(course=course).order_by('id'),
        'filters': [{'visible_name': f.visible_name, 'value': f.value}
                    for f in Filter.objects.filter(active=True)],
    }
    return render(request, 'definitions/view_course.html', context)

