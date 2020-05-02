from django.shortcuts import render, get_object_or_404, get_list_or_404
import markdown
from .models import Article, Category, Tag
from django.views.generic import DetailView, ListView
from django.urls import reverse
from comment.forms import CommentForm
from django.db.models import Q
from haystack.generic_views import SearchView as HaySearchView


class ArticleBaseList(ListView):
    template_name = 'index.html'
    model = Article
    ordering = ['-create_time']
    paginate_by = 1

    def get_queryset(self):
        queryset = super(ArticleBaseList, self).get_queryset()
        return queryset.filter(status=0)

    def get_context_data(self, **kwargs):
        context = super(ArticleBaseList, self).get_context_data(**kwargs)
        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 关于什么是 Paginator，Page 类在 Django Pagination 简单分页：http://zmrenwu.com/post/34/ 中已有详细说明。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}

            # 当前页左边连续的页码号，初始值为空
        left = []

        # 当前页右边连续的页码号，初始值为空
        right = []

        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False

        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 2]

            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data

class CategoryView(ArticleBaseList):
    cate = None

    def get_queryset(self):
        return super(CategoryView, self).get_queryset().filter(category=self.cate)

    def get_context_data(self, **kwargs):
        context = super(ArticleBaseList, self).get_context_data(**kwargs)
        context.update({'breadcrumb_name': '分类', 'breadcrumb_item': self.cate, })
        return context

    def get(self, request, *args, **kwargs):
        self.cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        response = super(CategoryView, self).get(request, *args, **kwargs)
        return response


class TagView(ArticleBaseList):
    tag = None

    def get_queryset(self):
        self.request.GET.get('q')
        return super(TagView, self).get_queryset().filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context.update({'breadcrumb_name': 'Tag标签', 'breadcrumb_item': self.tag, })
        return context

    def get(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get(request, *args, **kwargs)


class SearchView(ArticleBaseList):
    q = ''

    def get_queryset(self):
        if not self.q:
            return None
        queryset = super(SearchView, self).get_queryset()
        sql_title = {'{0}__{1}'.format('title', 'icontains'): self.q}
        sql_body = {'{0}__{1}'.format('body', 'icontains'): self.q}
        sql_body_1 = {'{0}__{1}'.format('body_1', 'icontains'): self.q}
        return queryset.filter(Q(**sql_title) | Q(**sql_body) | Q(**sql_body_1))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update({'breadcrumb_name': '搜索关键词', 'breadcrumb_item': {
            'get_absolute_url': reverse('article:search') + '?{}={}'.format('q', self.q),
            'name': '【{}】'.format(self.q),
        }})
        return context

    def get(self, request, *args, **kwargs):
        self.q = self.request.GET.get('q')
        return super(SearchView, self).get(request, *args, **kwargs)

class ArchivesView(ArticleBaseList):
    def get_queryset(self):
        return super(ArchivesView, self).get_queryset().filter(create_time__year=self.kwargs.get('year'), create_time__month=self.kwargs.get('month'))

    def get_context_data(self, **kwargs):
        context = super(ArchivesView, self).get_context_data(**kwargs)
        context.update({'breadcrumb_name': '归档', 'breadcrumb_item': {
            'get_absolute_url': reverse('article:archives', kwargs={'year': self.kwargs.get('year'), 'month': self.kwargs.get('month')}),
            'name': '{}-{}'.format(self.kwargs.get('year'), self.kwargs.get('month')),
        }})
        return context


class IndexView(ArticleBaseList):
    pass


class PostDetailView(DetailView):
    model = Article
    template_name = 'detail.html'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.inc_views()
        return response

    def get_object(self, queryset=None):
        obj = super(PostDetailView, self).get_object(queryset)
        if obj.body_type == 1:
            obj.body = markdown.markdown(obj.body_1,
                                         extensions=[
                                             'markdown.extensions.extra',
                                             'markdown.extensions.codehilite',
                                             'markdown.extensions.toc',
                                         ])
        return obj

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        comment_form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'comment_form': comment_form,
            'comment_list': comment_list,
        })
        return context



def search(request):
    q = request.GET.get('q')
    print(q)

    error_msg = ''
    if not q:
        error_msg = '请输入关键词'
        return render(request, 'index.html', {'error_msg': error_msg})

    post_list = Article.objects.filter(Q(title__icontains=q) | Q(body___icontains=q) | Q(body_1___icontains=q))
    return render((request, 'index.html', {'error_msg': error_msg, 'post_list': post_list}))



class HayStackSearchView(HaySearchView):
    template_name = 'search.html'
    def get_context_data(self, **kwargs):
        context = super(HayStackSearchView, self).get_context_data(**kwargs)
        context.update({'breadcrumb_name': '搜索关键词', 'breadcrumb_item': {
            'get_absolute_url': reverse('article:search_view') + '?{}={}'.format('q', self.request.GET.get('q')),
            'name': '【{}】'.format(self.request.GET.get('q')),
        }})
        return context