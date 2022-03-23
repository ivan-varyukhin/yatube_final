from django.contrib import admin

from posts.models import Post, Group, Comment, Follow


admin.site.site_header = 'Администрирование сайта'
admin.site.site_title = 'Управление Yatube'
admin.site.index_title = 'Управление Yatube'

class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    list_editable = ('slug',)
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = '-пусто-'

class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "text", "created",)
    search_fields = ("post",)
    list_filter = ("author", "created",)


class FollowAdmin(admin.ModelAdmin):
    list_display = ("author", "user",)
    list_filter = ("author", "user",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
