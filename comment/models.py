from django.db import models
from article.models import Article

# Create your models here.


class Comment(models.Model):
    name = models.CharField(max_length=32, verbose_name='昵称')
    email = models.EmailField(verbose_name='Email')
    ctext = models.TextField('内容')
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    article = models.ForeignKey(Article)

    def __repr__(self):
        return '<Comment : {} {} {}>'.format(self.name, self.created_at, self.ctext[:20])

    __str__ = __repr__

    class Meta:
        verbose_name = "评论信息"
        verbose_name_plural = "评论信息"