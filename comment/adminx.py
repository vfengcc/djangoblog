import xadmin
from .models import Comment


class CommentAdmin:
    list_display = ['name', 'email', 'ctext', 'created_at']


xadmin.site.register(Comment, CommentAdmin)
# xadmin.site.register(Comment)
