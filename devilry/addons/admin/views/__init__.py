from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms

from devilry.core.models import Node, Subject, Period, Assignment
from devilry.ui.widgets import DevilryDateTimeWidget, \
    DevilryMultiSelectFewUsersDb
from devilry.ui.fields import MultiSelectCharField

from shortcuts import EditBase, deletemany_generic


@login_required
def edit_node(request, obj_id=None, successful_save=False):
    return EditNode(request, obj_id, successful_save).create_view()

@login_required
def edit_subject(request, obj_id=None, successful_save=False):
    return EditSubject(request, obj_id, successful_save).create_view()

@login_required
def edit_period(request, obj_id=None, successful_save=False):
    return EditPeriod(request, obj_id, successful_save).create_view()


@login_required
def delete_manynodes(request):
    return deletemany_generic(request, Node)

@login_required
def delete_manysubjects(request):
    return deletemany_generic(request, Subject)

@login_required
def delete_manyperiods(request):
    return deletemany_generic(request, Period)

@login_required
def delete_manyassignments(request):
    return deletemany_generic(request, Assignment)


class EditNode(EditBase):
    VIEW_NAME = 'node'
    MODEL_CLASS = Node

    def create_form(self):
        class NodeForm(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=False,
                    queryset = Node.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False)
            class Meta:
                model = Node
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
        return NodeForm


class EditSubject(EditBase):
    VIEW_NAME = 'subject'
    MODEL_CLASS = Subject

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Node.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False)
            class Meta:
                model = Subject
                fields = ['parentnode', 'short_name', 'long_name', 'admins']
        return Form


class EditPeriod(EditBase):
    VIEW_NAME = 'period'
    MODEL_CLASS = Period

    def create_form(self):
        class Form(forms.ModelForm):
            parentnode = forms.ModelChoiceField(required=True,
                    queryset = Subject.where_is_admin(self.request.user))
            admins = MultiSelectCharField(widget=DevilryMultiSelectFewUsersDb, 
                                          required=False)
            class Meta:
                model = Period
                fields = ['parentnode', 'short_name', 'long_name', 'start_time', 'end_time', 'admins']
                widgets = {
                    'start_time': DevilryDateTimeWidget,
                    'end_time': DevilryDateTimeWidget,
                    }
        return Form
