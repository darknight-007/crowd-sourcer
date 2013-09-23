from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/$', 'wgpoll.views.index'),
    url(r'^polls/vote/$', 'wgpoll.views.vote'),
    url(r'^polls/report/$', 'wgpoll.views.report'),
    url(r'^polls/getvotes/$', 'wgpoll.views.getvotes'),
    url(r'^polls/getballots/$', 'wgpoll.views.getballots'),
    url(r'^polls/dash/$', 'wgpoll.dashView.index'),
    url(r'^polls/dash/update/$', 'wgpoll.dashView.update'),
    url(r'^admin/', include(admin.site.urls)),
)
