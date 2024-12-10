from django.contrib import admin
from .models import LastFormCreated, VerificationLink, People, Post, Comment , IPCRFForm , COTForm , RPMSFolder , RPMSClassWork , RPMSAttachment, School, MainAdmin, PostAttachment

# Register your models here.

admin.site.register(VerificationLink)
admin.site.register(MainAdmin)
admin.site.register(School)

admin.site.register(People)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostAttachment)


admin.site.register(IPCRFForm)
admin.site.register(COTForm)
admin.site.register(RPMSFolder)
admin.site.register(RPMSClassWork)
admin.site.register(RPMSAttachment)
admin.site.register(LastFormCreated)
