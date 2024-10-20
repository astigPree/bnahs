from django.contrib import admin
from .models import People, Post, Comment , IPCRFForm , COTForm , RPMSFolder , RPMSClassWork , RPMSAttachment

# Register your models here.

admin.site.register(People)
admin.site.register(Post)
admin.site.register(Comment)


admin.site.register(IPCRFForm)
admin.site.register(COTForm)
admin.site.register(RPMSFolder)
admin.site.register(RPMSClassWork)
admin.site.register(RPMSAttachment)

