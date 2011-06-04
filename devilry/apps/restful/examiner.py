from django import forms

from ..simplified.examiner import (Subject, Period, Assignment, Group)
import fields
from restview import RestView
from base import SearchFormBase


class RestSubject(RestView):
    SIMPCLASS = Subject

    def restultqry_to_list(self, resultQry):
        tpl = '/%(short_name)s'
        def filter_func(assignmentDict):
            assignmentDict.update(path=tpl % assignmentDict)
            #assignmentDict.update(id=tpl % assignmentDict)
            return assignmentDict
        return filter(filter_func, resultQry)

    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Subject.get_default_ordering())


class RestPeriod(RestView):
    SIMPCLASS = Period

    def restultqry_to_list(self, resultQry):
        tpl = '/%(parentnode__short_name)s/%(short_name)s'
        def filter_func(assignmentDict):
            assignmentDict.update(path=tpl % assignmentDict)
            #assignmentDict.update(id=tpl % assignmentDict)
            return assignmentDict
        return filter(filter_func, resultQry)

    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Subject.get_default_ordering())
        subject_short_name = forms.CharField(required=False)


class RestAssignment(RestView):
    SIMPCLASS = Assignment

    def restultqry_to_list(self, resultQry):
        tpl = ('/%(parentnode__parentnode__short_name)s/'
            '%(parentnode__short_name)s/%(short_name)s')
        def filter_func(assignmentDict):
            assignmentDict.update(path=tpl % assignmentDict)
            return assignmentDict
        return filter(filter_func, resultQry)

    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Assignment.get_default_ordering())
        old = fields.BooleanWithFallbackField(fallbackvalue=True)
        active = fields.BooleanWithFallbackField(fallbackvalue=True)
        longnamefields = fields.BooleanWithFallbackField()
        pointhandlingfields = fields.BooleanWithFallbackField()
        subject_short_name = forms.CharField(required=False)
        period_short_name = forms.CharField(required=False)


class RestGroup(RestView):
    SIMPCLASS = Group
    class SearchForm(SearchFormBase):
        orderby = fields.CharListWithFallbackField(
                fallbackvalue=Group.get_default_ordering())
        deadlines = fields.BooleanWithFallbackField(fallbackvalue=False)
