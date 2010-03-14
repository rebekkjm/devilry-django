from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period', 'assignment'):
    generic_urls += [
        url(r'^%ss/edit/(?P<node_id>\d+)$' % x, 'views.edit_%s' % x,
            name='devilry-admin-edit_%s' % x),
        url(r'^%ss/add/$' % x, 'views.edit_%s' % x,
            name='devilry-admin-add_%s' % x),
        url(r'^%ss/$' % x, 'views.list_%ss' % x,
            name='devilry-admin-list_%ss' % x)]

urlpatterns = patterns('devilry.addons.adminview',
    (r'^$', 'views.main'),
    *generic_urls
)