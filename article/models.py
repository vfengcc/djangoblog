import datetime
import time
import markdown
from django.utils.html import strip_tags
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from users.models import UserProfile as User

from DjangoUeditor.models import UEditorField

class Category(models.Model):
    # 状态类别
    CATEGORY_TYPE = (
        (0, "启用"),
        (1, "关闭"),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField("名称", max_length=64)
    created_at = models.DateTimeField("添加时间", auto_now_add=True)
    status = models.IntegerField("状态", default=0, choices=CATEGORY_TYPE)

    def __repr__(self):
        return self.name

    __str__ = __repr__

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = "文章分类"

    def get_absolute_url(self):
        return reverse('article:category', kwargs={'pk': self.pk})


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=100)

    def __repr__(self):
        return self.name

    __str__ = __repr__

    class Meta:
        verbose_name = "Tag标签"
        verbose_name_plural = "Tag标签"

    def get_absolute_url(self):
        return reverse('article:tag', kwargs={'pk': self.pk})


def upload_to_goods_img(instance, filename):
    date = datetime.datetime.now()
    format_ = "%Y%m%d"
    date_str = date.strftime(format_)  # 格式化时间
    today_str = f"{str(date_str)}"   # 时间转成字符串
    return 'article/{today_str}/{prefix}_{filename}.{suffix}'.format(today_str=today_str,
                                                                     prefix='article',
                                                                     filename=int(time.time() * 1000),
                                                                     suffix=filename.split('.')[-1])


class Article(models.Model):
    # 状态
    CATEGORY_TYPE = (
        (0, "显示"),
        (1, "禁用"),
    )
    # 内容类型
    CONTENT_TYPE = (
        (0, "Ueditor"),
        (1, "MarkDown"),
    )
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    title = models.CharField("标题", max_length=128)
    description = models.CharField("描述", max_length=256, blank=True)
    title_img = models.ImageField("图片", upload_to=upload_to_goods_img, null=True, blank=True)

    body_type = models.PositiveSmallIntegerField(verbose_name='内容类型', default=0, choices=CONTENT_TYPE)
    body = UEditorField(verbose_name='内容详情', width=600, height=300, toolbars="full", imagePath='article/image',
                           filePath="course/ueditor/", upload_settings={"imageMaxSize": 1204000}, default='', null=True, blank=True)
    body_1 = models.TextField(verbose_name='内容详情(MarkDown)', blank=True, null=True)

    tags = models.ManyToManyField(Tag, blank=True)
    views = models.PositiveIntegerField(verbose_name='阅读数', default=0)
    status = models.IntegerField('状态', default=0, choices=CATEGORY_TYPE)
    create_time = models.DateTimeField("发表时间")
    update_time = models.DateTimeField("修改时间")

    # 增加浏览量
    def inc_views(self):
        self.views = F('views') + 1
        self.save()
        # 刷新后立即生效
        self.refresh_from_db(fields=['views'])

    def get_absolute_url(self):
        return reverse('article:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.update_time = timezone.now()
        if self.id is None:
            self.create_time = self.update_time

        if not self.description:
            if self.body_type == 1:
                body = markdown.Markdown(extensions=[
                    'markdown.extensions.extra',
                    'markdown.extensions.codehilite',
                ]).convert(self.body_1)
            else:
                body = self.body
            self.description = strip_tags(body)[:64]
        return super(Article, self).save(*args, **kwargs)

    def __repr__(self):
        return self.title

    __str__ = __repr__

    class Meta:
        verbose_name = "文章信息"
        verbose_name_plural = "文章信息"
        ordering = ["-create_time"]

