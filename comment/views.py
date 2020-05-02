from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest

from .forms import CommentForm
from article.models import Article


def article_comment(request: HttpRequest, article_pk):
    # 校验article是否存在
    article = get_object_or_404(Article, pk=article_pk)
    if request.method == 'POST':
        # 赋值到表单
        form = CommentForm(request.POST)
        # 表单验证
        if form.is_valid():
            # 构建comment模型，不提交保存
            comment = form.save(commit=False)
            # 关联post
            comment.article = article
            # 保存提交
            comment.save()
            # 重定向post详情页， post模型 会调用get_absolute_url
            return redirect(article)
        else:
            comment_list = article.comment_set.all()
            context = {
                'post': article,
                'comment_form': form,
                'comment_list': comment_list
            }
            return render(request, 'detail.html', context=context)
    else:
        # 无提交动作，直接重定向到post详情页面
        return redirect(article)
