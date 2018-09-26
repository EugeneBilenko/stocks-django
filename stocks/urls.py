from django.conf.urls import url

from . import views

app_name = 'stocks'
urlpatterns = [
    url(r'^$', views.stocks, name='homepage'),
    url(r'^table_view/$', views.table_view, name='table_view'),
    url(r'^graph/(?P<algo_name>\w+)/$', views.graph, name='graph'),
]