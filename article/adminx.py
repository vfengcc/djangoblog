import xadmin
from xadmin import views
from .models import Article, Category, Tag


# 开启后台主题样式选择
class BaseSetting(object):
    enable_themes = True
    user_bootswatch = True


# 后台全局设置
class GlobalSettings(object):
    # 后台标签
    site_title = '一起开发网 - 博客'
    # 后台页脚
    site_footer = '一起开发网 www.17kaifa.com'
    # 菜单样式设置
    # menu_style = "accordion"


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)

from xadmin.layout import Fieldset


class ArticleAdmin:
    # 控制展示的字段
    list_display = ['category', 'title', 'create_time', 'description', 'title_img']

    list_display_links = ['title']

    # 创建和修改是展示的字段
    # fields
    # 可以查询的字段
    search_fields = ['title', 'create_time']
    # actions 操作动作

    style_fields = {'body': 'ueditor'}

    exclude = ['create_time', 'update_time', 'views', 'user']


    # 直接编辑
    #list_editable = ['article']

    #重写过滤显示，只显示status=0的信息
    def get_context(self):
        context = super(ArticleAdmin, self).get_context()
        if 'form' in context:
            context['form'].fields['category'].queryset = Category.objects.filter(status=0)
        return context

    def save_models(self):
        obj = self.new_obj
        obj.user = self.request.user
        obj.save()

    # 重写admin删除中调用的是这样方法，修改model为逻辑删除
    def delete_model(self, request, obj):
        obj.status = 1
        obj.save()
    #
    # class Media:
    #     js = (
    #         '/static/kindeditor/kindeditor-min.js',
    #         '/static/kindeditor/lang/zh_CN.js',
    #         '/static/kindeditor/config.js'
    #     )


class CategoryAdmin:
    list_display = ['name', 'created_at', 'status']
    search_fields = ['name', 'created_at']

class TagAdmin:
    list_display = ['name']
    search_fields = ['name']

xadmin.site.register(Article, ArticleAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(Tag, TagAdmin)