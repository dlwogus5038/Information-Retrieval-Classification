from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/page/$', views.page, name='page'),
    url(r'^search/page/show_cluster/$', views.show_cluster, name='show_cluster'),
]