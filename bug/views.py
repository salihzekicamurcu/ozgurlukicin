#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Artistanbul
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.core.mail import send_mail

from oi.st.wrappers import render_response
from oi.forum.views import flood_control
from oi.bug.models import Bug, Comment
from oi.bug.forms import BugForm, FullBugForm, CommentForm
from oi.bug.settings import BUGS_PER_PAGE
from oi.settings import DEFAULT_FROM_EMAIL

BUG_MAILLIST = User.objects.get(name="akin").email

@login_required
def add_bug(request):
    if request.method == "POST":
        form = BugForm(request.POST.copy())
        flood, timeout = flood_control(request)

        if form.is_valid() and not flood:
            bug = Bug(
                title = form.cleaned_data["title"],
                submitter = request.user,
                description = form.cleaned_data["description"],
                priority = form.cleaned_data["priority"],
                assigned_to = User.objects.get(username="akin"),
                )
            bug.save()
            email_dict = {
                    "bugId": bug.id,
                    "bugTitle": bug.title,
                    "link": bug.get_absolute_url(),
                    "title": bug.title,
                    "priority": bug.priority,
                    "submitter": "%s %s <%s>" % (bug.submitter.first_name, bug.submitter.last_name, bug.submitter.email),
                    "assigned_to": "%s %s <%s>" % (bug.assigned_to.first_name, bug.assigned_to.last_name, bug.assigned_to.email),
                    "description": bug.description,
                    }
            email_subject = u"[Hata %(bugId)s] Yeni: %(bugTitle)s"
            email_body = u"""%(link)s
Başlık: %(title)s
Öncelik: P%(priority)s
Bildiren: %(submitter)s
Atanan: %(assigned_to)s

%(description)s
"""
            mail_set = set()
            mail_set.add(BUG_MAILLIST)
            mail_set.add(bug.submitter.email)
            mail_set.add(bug.assigned_to.email)
            send_mail(email_subject % email_dict, email_body % email_dict, DEFAULT_FROM_EMAIL, list(mail_set), fail_silently=True)
            return HttpResponseRedirect(bug.get_absolute_url())
    else:
        form = BugForm(auto_id=True)
    return render_response(request, 'bug/bug_add.html', locals())

@permission_required('bug.change_bug', login_url="/kullanici/giris/")
def change_bug(request, id):
    bug = Bug.objects.get(id=id)
    if request.method == "POST":
        form = FullBugForm(request.POST.copy())
        if form.is_valid():
            bug.title = form.cleaned_data["title"]
            bug.description = form.cleaned_data["description"]
            bug.priority = form.cleaned_data["priority"]
            bug.status = form.cleaned_data["status"]
            bug.assigned_to = form.cleaned_data["assigned_to"]
            bug.save()
    return HttpResponseRedirect(bug.get_absolute_url())

def main(request):
    bugs = Bug.objects.order_by("status")
    return object_list(request, bugs,
            template_name = "bug/bug_main.html",
            template_object_name = "bug",
            paginate_by = BUGS_PER_PAGE,
            allow_empty = True,
            )

def detail(request, id):
    bug = Bug.objects.get(id=id)
    default_data = {
            "title": bug.title,
            "assigned_to": bug.assigned_to.id,
            "description": bug.description,
            "status": bug.status,
            "priority": bug.priority,
            }
    bugform = FullBugForm(default_data)
    if request.method == "POST" and request.user.is_authenticated():
        form = CommentForm(request.POST.copy())
        flood, timeout = flood_control(request)

        if form.is_valid() and not flood:
            comment = Comment(
                bug = bug,
                author = request.user,
                text = form.cleaned_data["text"],
                )
            comment.save()
    else:
        form = CommentForm()
    return render_response(request, 'bug/bug_detail.html', locals())
