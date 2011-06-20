from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

import restful
import views

urlpatterns = patterns('devilry.apps.tutorialstats',
    url(r'^rest/(?P<pk>\d+)?$',
        login_required(restful.RestStatConfig.as_view()),
        name='devilry-tutorialstats-rest'),
    url(r'^$',
        login_required(views.main),
        name='devilry-tutorialstats-main'),
)