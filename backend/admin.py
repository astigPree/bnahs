from django.contrib import admin
from .models import People, Post, Comment

# Register your models here.

admin.site.register(People)
admin.site.register(Post)
admin.site.register(Comment)


