from django.conf.urls import patterns, url

from dispatch_web import views

urlpatterns = patterns('',

    ## HOME
    # ex: /dispatch/
    url(r'^$', views.home, name='home'),
    url(r'^active/$', views.all_active, name='all_active'),
    url(r'^completed/$', views.all_completed, name='all_completed'),
    url(r'^stats/$', views.stats, name='stats'),
#    url(r'^ajax_active/$', views.ajax_update_active),
#    url(r'^ajax_completed/$', views.ajax_update_completed),

    ## POLLERS
    # ex: /dispatch/pollers/
    url(r'^pollers/$', views.pollers, name='pollers'),
    # ex: /dispatch/pollers/new
    url(r'^pollers/new/$', views.add_poller, name='add_poller'),
    # ex: /dispatch/pollers/5/
    url(r'^pollers/(?P<poller_id>\d+)/$', views.poller_detail, name='poller_detail'),
    # ex: /dispatch/pollers/5/delete/
    url(r'^pollers/(?P<poller_id>\d+)/delete/$', views.delete_poller, name='delete_poller'),
    # ex: /dispatch/pollers/5/edit/
    url(r'^pollers/(?P<poller_id>\d+)/edit/$', views.edit_poller, name='edit_poller'),
    # ex: /dispatch/pollers/5/enable/
    url(r'^pollers/(?P<poller_id>\d+)/enable/$', views.enable_poller, name='enable_poller'),
    # ex: /dispatch/pollers/5/disable/
    url(r'^pollers/(?P<poller_id>\d+)/disable/$', views.disable_poller, name='disable_poller'),

    ## SEARCH
    # ex: /dispatch/search/
    url(r'^search/$', views.search, name='search'),

    ## SERVERS
    # ex: /dispatch/servers/
    url(r'^servers/$', views.servers, name='servers'),
    # ex: /dispatch/servers/5/delete/
    url(r'^servers/(?P<server_id>\d+)/delete/$', views.delete_server, name='delete_server'),
)






#    # ex: /polls/5/
#    url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
#    # ex: /polls/5/results/
#    url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
#    # ex: /polls/5/vote/
#    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),

