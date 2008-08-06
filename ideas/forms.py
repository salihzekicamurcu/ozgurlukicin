#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import newforms as forms
from oi.ideas.models import Idea, RelatedCategory
from oi.st.forms import XssField

class CommentForm(forms.Form):
    text = forms.CharField(label="Yorumunuz", required=True, widget=forms.Textarea(attrs={ 'cols':'83%', 'rows':'7'}))

class NewIdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        exclude = ("submitter", "status","vote_count", "duplicate",  "slug", "is_hidden")

#    def __init__(self,*args,**kwargs):
#        super(NewIdeaForm, self).__init__(*args, **kwargs)
#        related_categories = RelatedCategory.objects.all()
#        self.fields['related_to'].choices=[for cat ]
