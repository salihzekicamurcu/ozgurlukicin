#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2008 TÜBİTAK UEKAE
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django import template
from django.template import Context, loader
from oi.tema.models import ThemeItem, ThemeAbuseReport

register = template.Library()

@register.simple_tag
def number_of_theme_abuse():
    return ThemeAbuseReport.objects.count()

@register.simple_tag
def top_content():
    object_list = ThemeItem.objects.filter(status=True).order_by("-rating", "-update")[:10]
    return loader.get_template("tema/sidebar.html").render(Context({"object_list":object_list}))
