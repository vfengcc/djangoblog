from django.conf.urls import url, include
from django.contrib import admin
from . import views

app_name = 'article'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>\d+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^category/(?P<pk>\d+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^archives/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.ArchivesView.as_view(), name='archives'),
    url(r'^tag/(?P<pk>\d+)/$', views.TagView.as_view(), name='tag'),
    # url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^search/?$', views.HayStackSearchView.as_view(), name='search_view'),
]
