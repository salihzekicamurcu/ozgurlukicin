#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2010 TÜBİTAK UEKAE
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django.http import HttpResponse, HttpResponseRedirect
from oi.beyin2.models import Idea, Status, Category, Vote
from oi.beyin2.forms import IdeaForm, IdeaDuplicateForm, ScreenShotForm
from oi.st.wrappers import render_response
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from oi.forum.models import Topic, Forum, Post
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator

DefaultCategory = 1
DefaultStatus = 1
idea_per_page = 2
# if it doesnot exist ??
ForumCategory = "Yeni Fikirler"

def main(request, idea_id = -1,page_number = 1, order = "date"):
    if request.POST:
        idea = get_object_or_404(Idea, pk = idea_id)
        idea.status = get_object_or_404(Status, name = request.POST['status'])
        idea.category = get_object_or_404(Category, name = request.POST['category'])
        idea.save()
        """idea_list = Idea.objects.filter(is_hidden=False).order_by('-dateSubmitted')[:10]
        status_list = Status.objects.all()
        category_list = Category.objects.all()
        return render_response(request,'beyin2/idea_list.html',{'idea_list': idea_list, 'status_list':status_list, 'category_list': category_list})
        """
        return HttpResponseRedirect(reverse('oi.beyin2.views.main'))
    else:
        #idea list order changes
        if order == "date":
            all_idea_list = Idea.objects.filter(is_hidden=False).order_by('-dateSubmitted')
        elif order == "vote_value":
            all_idea_list = Idea.objects.filter(is_hidden=False).order_by('vote_value')
        elif order == "vote_count":
            all_idea_list = Idea.objects.filter(is_hidden=False).order_by('vote_count')
        elif order == "title":
            all_idea_list = Idea.objects.filter(is_hidden=False).order_by('title')
        status_list = Status.objects.all()
        category_list = Category.objects.all()
        paginator = Paginator(all_idea_list, idea_per_page)
        idea_list=paginator.page(page_number)
        return render_response(request,'beyin2/idea_list.html',{'idea_list': idea_list, 'status_list':status_list, 'category_list': category_list,'order':order})



def idea_detail(request,idea_id):
    idea = get_object_or_404(Idea, pk = idea_id)
    if idea.is_hidden:
        return HttpResponse("Missing idea")
    status_list = Status.objects.all()
    category_list = Category.objects.all()
    return render_response(request,'beyin2/idea_alone.html',{'idea': idea, 'status_list':status_list, 'category_list': category_list,})


def vote(request, idea_id, vote ,come_from):
    if vote == "1":
        vote_choice = "U"
    elif vote == "0":
        vote_choice = "N"
    elif vote == "2":
        vote_choice = "D"

    voter = request.user
    idea = get_object_or_404(Idea, pk = idea_id)
    working_vote = Vote.objects.filter( voter=voter, idea=idea )
    
    if working_vote.count() !=0:
        working_vote = working_vote[0]
        
        # if already voted choice removed from template, this control can also removed
        if vote_choice != working_vote.vote:
            #remove the old vote
            if working_vote.vote == "U":
                idea.vote_value -=10
            elif working_vote.vote == "D":
                idea.vote_value +=10
            else:
                idea.vote_value -=1
            # add new votes value
            if vote_choice == "U":
                idea.vote_value +=10
            elif vote_choice == "D":
                idea.vote_value -=10
            else:
                idea.vote_value +=1
        else:
            return HttpResponse("you have already voted, dont cheat!")
    else:
            if vote_choice == "U":
                idea.vote_value +=10
            elif vote_choice == "D":
                idea.vote_value -=10
            else:
                idea.vote_value +=1
            #and for every vote add 1
            idea.vote_value +=1
            working_vote = Vote.objects.create( voter=voter, idea=idea, vote=vote_choice )
    idea.save()
    working_vote.vote = vote_choice
    working_vote.save()
    if come_from == "detail":
        return HttpResponseRedirect(reverse('oi.beyin2.views.idea_detail', args=(idea_id,)))
    return HttpResponseRedirect(reverse('oi.beyin2.views.main'))

@login_required
def add_new(request):
    try:
        form = IdeaForm({'title': '', 'description': '', 'status': DefaultStatus, 'category': DefaultCategory}, prefix = 'ideaform')
        ScreenShotSet = formset_factory(ScreenShotForm, extra=3, max_num=3)
        if request.POST:
            try:
                form = IdeaForm(request.POST, prefix = 'ideaform')
            except:
                return HttpResponse("forum  does not exist")
            ScreenShotFormSet = ScreenShotSet(request.POST, request.FILES, prefix = 'imageform')
            if form.is_valid() and  ScreenShotFormSet.is_valid():
                forum = Forum.objects.get(name = ForumCategory)
                topic = Topic(forum = forum,title = form.cleaned_data['title'])
                topic.save()

                idea = form.save(commit = False)
                idea.submitter = request.user
                idea.topic = topic
                idea.save()

                for screenshotform in ScreenShotFormSet.forms:
                        image = screenshotform.save(commit = False)
                        if image.image:
                            image.idea = idea
                            image.save()

                post_text = "<p>#" + str(idea.id) + " "
                post_text += idea.title + "</p>"
                post_text += "<p>" + idea.description + "</p>"
                post_text += "<p>" + idea.description + "</p>"
                for image in idea.screenshot_set.all():
                    post_text += '<img src="'+image.image.url+'" height="320" width"240" /><br />'
                post = Post(topic=topic, author=request.user, text=post_text )
                post.save()
                topic.topic_latest_post = post
                topic.posts = 1
                topic.save()
                topic.forum.forum_latest_post = post
                topic.forum.topics += 1
                topic.forum.posts += 1
                topic.forum.save()
                return HttpResponseRedirect(reverse('oi.beyin2.views.main'))
            else:
                return render_response(request, 'beyin2/idea_errorpage.html',{'error':form.errors,})
        else:
            ScreenShotFormSet = ScreenShotSet(prefix = 'imageform')
            return render_response(request, 'beyin2/idea_new.html', {'form':form,'ScreenShotFormSet':ScreenShotFormSet})
    except:
        return render_response(request, 'beyin2/idea_errorpage.html',{'error':form.errors,})

@permission_required('beyin2.change_idea')
def edit_idea(request, idea_id):
    try:
        idea = get_object_or_404(Idea, pk=idea_id)
        form = IdeaForm({'title': idea.title, 'description': idea.description, 'status': idea.status.id, 'category': idea.category.id})
        if request.POST:
            form = IdeaForm(request.POST)
            if form.is_valid():
                """
                i = form.save(commit = False, instance=idea)
                i.submitter = request.user
                
                i.save()
                """
                i = IdeaForm(request.POST, instance = idea)
                i.save()
                return HttpResponseRedirect(reverse('oi.beyin2.views.main'))
            else:
                return render_response(request, 'beyin2/idea_errorpage.html')
        else:

            return render_response(request, 'beyin2/idea_edit.html', {'form':form, 'idea':idea})
    except:
        return render_response(request, 'beyin2/idea_errorpage.html')


def delete_idea(request, idea_id):
    idea = Idea.objects.get(pk=idea_id)
    idea.is_hidden = True
    idea.save()
    
    # and lock the topic from forum
    if idea.topic.locked:
        return HttpResponse("already locked?")
    else:
        idea.topic.locked = 1
        idea.topic.save()
    
    return HttpResponseRedirect(reverse('oi.beyin2.views.main'))
    
def mark_duplicate(request, idea_id):
    if request.POST:
        idea = get_object_or_404(Idea, pk = idea_id)
        if request.POST['dupple_number']:
            idea_original = get_object_or_404(Idea, pk= int(request.POST['dupple_number']))
            idea.duplicate = idea_original
        else:
            idea_original = get_object_or_404(Idea, pk = int(request.POST['dupple']))
            idea.duplicate = idea_original
        idea.is_duplicate = True
        idea.save()
        #changes for forum
        #the duplicate
        topic = idea.topic
        post_text = "<h1> This idea marked duplicate to another idea </h1>"
        post_text += "<p>#" + str(idea_original.id) + " "
        post_text += idea_original.title + "</p>"
        post_text += "<p>" + idea_original.description + "</p>"
        post_text += "<br /> <h1>continue on this forum instead please</h1>"
        for image in idea_original.screenshot_set.all():
            post_text += '<img src="'+image.image.url+'" height="320" width"240" /><br />'
        post = Post(topic=topic, author=request.user, text=post_text )
        post.save()
        topic.topic_latest_post = post
        topic.save()
        topic.forum.forum_latest_post = post
        topic.forum.posts += 1
        topic.forum.save()
        #the original idea
        topic = idea_original.topic
        post_text = "<h1> Another idea marked duplicate to this idea </h1>"
        post_text += "<p>#" + str(idea.id) + " "
        post_text += idea.title + "</p>"
        post_text += "<p>" + idea.description + "</p>"
        for image in idea.screenshot_set.all():
            post_text += '<img src="'+image.image.url+'" height="320" width"240" /><br />'
        post = Post(topic=topic, author=request.user, text=post_text )
        post.save()
        topic.topic_latest_post = post
        topic.save()
        topic.forum.forum_latest_post = post
        topic.forum.posts += 1
        topic.forum.save()
        return HttpResponseRedirect(reverse('oi.beyin2.views.delete_idea', args=(idea.id,)))
    else:
        idea = get_object_or_404(Idea, pk = idea_id)
        idea_list = Idea.objects.exclude(pk=idea.id).filter(is_hidden=False)
        return render_response(request, 'beyin2/idea_duplicate.html', {'idea': idea,'idea_list': idea_list})


