from django import template
from django.db.models.aggregates import Count
from ..models import Article, Category, Tag


register = template.Library()

@register.simple_tag
def get_recent_articles(num=2):
    return Article.objects.all().order_by('-create_time')[:num]

@register.simple_tag
def get_tags(num=10):
    return Tag.objects.annotate(article_nums=Count('article')).order_by('-article_nums')[:num]

@register.simple_tag
def get_categories():
    return Category.objects.annotate(article_nums=Count('article'))

@register.simple_tag
def get_archives():
    ''' 归档模板标签，字段、精度、排序  '''
    return Article.objects.dates('create_time', 'month', order='DESC')

