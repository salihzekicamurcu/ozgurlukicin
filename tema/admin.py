#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2009 TÜBİTAK UEKAE
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django.contrib import admin
from oi.tema.models import *

class ThemeItemAdmin(admin.ModelAdmin):
    fieldsets = (
            (None, {
                "fields": ("thumbnail", "title", "slug", "text", "changelog", "status", "tags")
                }),
            ("Diğer", {
                "classes": "collapse",
                "fields": ("author", "license", "rating", "download_count", "submit", "update", "comment_enabled")
                })
            )
    list_display = ("title", "author", "license", "status")
    list_display_links = ("title",)
    list_filter = ("status", "comment_enabled")
    search_fields = ["title", "text", "changelog"]

    class Media:
        js = ("js/jquery-1.2.6.min.js", "js/temaimages.js", "js/jquery.autocomplete.js", "js/taghelper.js")
        css = {
            "all": ("css/new/autocomplete.css",),
        }

class WallpaperAdmin(ThemeItemAdmin):
    fieldsets = (
            (None, {
                "fields": ("thumbnail", "title", "slug", "text", "changelog", "papers", "status", "tags")
                }),
            ("Diğer", {
                "classes": "collapse",
                "fields": ("author", "license", "rating", "download_count", "submit", "update", "comment_enabled")
                })
            )

class ThemeAbuseReportAdmin(admin.ModelAdmin):
    fieldsets = (
            (None, {
                "fields": ("themeitem","submitter","reason")
                }),
            )
    list_display = ("submitter","themeitem", "reason")
    list_filter = ("submitter",)
    search_fields = ["submitter","reason","post"]


admin.site.register(ThemeItem, ThemeItemAdmin)
admin.site.register(Wallpaper, WallpaperAdmin)
admin.site.register(WallpaperFile, admin.ModelAdmin)
admin.site.register(License, admin.ModelAdmin)
admin.site.register(ThemeAbuseReport, ThemeAbuseReportAdmin)
