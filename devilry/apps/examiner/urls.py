from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from restful import examiner_restful
from views import MainView, AssignmentGroupView

urlpatterns = patterns('devilry.apps.examiner',
                       url(r'^$', login_required(MainView.as_view()), name='examiner'),
                       url(r'^assignmentgroup/(?P<assignmentgroupid>\d+)$',
                           login_required(AssignmentGroupView.as_view()))
                      )

urlpatterns += examiner_restful
