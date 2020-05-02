from django.conf.urls import url
from . import views

app_name = 'comment'

urlpatterns = [
    url(r'^article_comment/(?P<article_pk>\d+)', views.article_comment, name='article_comment'),
]
