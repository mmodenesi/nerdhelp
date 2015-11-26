# -*- coding: utf-8 -*-
"""
Urls for app Definitions
"""

from django.conf.urls import patterns, url
from definitions.views import random_card
from definitions.views import view_card, edit_card, save_card, add_card
from definitions.views import rank_up, rank_down
from definitions.views import next_card, prev_card
from definitions.views import home, search
from definitions.views import view_course
from definitions.views import get_tags, autocomplete
from definitions.views import set_filter

urlpatterns = patterns(
    '',
    url(r'^home/$', home, name='home'),
    url(r'^course/(?P<course_id>\d+)$', view_course, name='view_course'),
    url(r'^random/$', random_card, name='random_card'),
    url(r'^search/$', search, name='search'),
    url(r'^card/(?P<card_id>\d+)$', view_card, name='view_card'),
    url(r'^next_card/(?P<card_id>\d+)/$', next_card, name='next_card'),
    url(r'^prev_card/(?P<card_id>\d+)/$', prev_card, name='prev_card'),
    url(r'^card/edit/(?P<card_id>\d+)$', edit_card, name='edit_card'),
    url(r'^card/add/$', add_card, name='add_card'),
    url(r'^save_card/$', save_card, name='save_card'),
    url(r'^rank-up/(?P<concept_id>\d+)/$', rank_up, name='rank_up'),
    url(r'^rank-down/(?P<concept_id>\d+)/$', rank_down, name='rank_down'),
    url(r'^get_tags/$', get_tags, name='get_tags'),
    url(r'^set_filter/$', set_filter, name='set_filter'),
    url(r'^autocomplete/$', autocomplete, name='autocomplete'),
)

