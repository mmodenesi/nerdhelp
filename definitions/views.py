# pylint: disable=multiple-statements, line-too-long
"""
Views for app definitions
"""
# python imports
import json
import operator
import random
import tempfile

# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django_ajax.decorators import ajax

# project imports
from definitions.models import Concept
from definitions.models import Course
from definitions.models import Filter
from definitions.models import Tag
from definitions.pdfutils import Latex2PdfException
from definitions.pdfutils import concepts2pdf


COURSE = 'C'
TYPE = 'T'
TAG = 'E'
LAST_RANDOM_CARD = None


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
        result.extend(Concept.objects.filter(name__icontains=query))
        result.extend(Concept.objects.filter(definition__icontains=query))
        result.extend(Concept.objects.filter(tags__name__icontains=query))

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
    if card:

        # find out most used type of concept
        types = Concept.objects.filter(
            course=card['course']
            ).values(
                'concept_type'
            ).annotate(
                dcount=Count('concept_type')
            ).order_by('-dcount')
        if types:
            card['concept_type'] = types[0]['concept_type']

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
        tags_instances = [Tag.objects.get_or_create(name=name)[0]
                          for name in tags_list]

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
    global LAST_RANDOM_CARD
    if LAST_RANDOM_CARD and concepts.count() > 1:
        print LAST_RANDOM_CARD
        concepts = concepts.exclude(pk=LAST_RANDOM_CARD)
    concepts = concepts.order_by('learning_coeff')
    concepts = concepts[:10]
    card = random.choice(concepts)
    LAST_RANDOM_CARD = card.id
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


def export_pdf(request):
    """Produce pdf document showing filtered cards"""
    card_id = request.GET.get('c')
    if card_id:
        concepts = Concept.objects.filter(pk=card_id)
    else:
        concepts = get_concepts_applying_filters()
    if not concepts:
        concepts = Concept.objects.all()

    _, path = tempfile.mkstemp(suffix='.pdf')
    try:
        concepts2pdf(concepts, path)
    except Latex2PdfException as e:
        context = {
            'error': str(e),
            'filters': [{'visible_name': f.visible_name, 'value': f.value}
                        for f in Filter.objects.filter(active=True)],
            }
        return render(request, 'definitions/pdferror.html', context)

    response = HttpResponse(FileWrapper(open(path, 'rb')),
                            content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="nerdhelp.pdf"'
    return response
