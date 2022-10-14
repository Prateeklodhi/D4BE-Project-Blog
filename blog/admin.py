from django.contrib import admin
from .models import Post,Comment
# Register your models here.
@admin.register(Post)#This decorator performs the same function as the admin.site.register() funstion
class PostAdmin(admin.ModelAdmin):
    list_display = ['title','slug','author','publish','status'] # this will add the following column on the admin site for Post taale
    list_filter = ['status','created','publish','author'] #This will add a filter block according to the given values that can be used to filter data according to the given values
    search_fields = ['title','body'] # this will add a search field to the admin site of Post table
    prepopulated_fields = {'slug':('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status','publish']
# admin.site.register(Post)
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','email','post','created','active']
    list_filter = ['active','created','updated']
    search_fields = ['name','email','body']