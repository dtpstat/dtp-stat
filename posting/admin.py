from django.contrib import admin

from posting.accounts import account
from posting import post
from .models import RegularPost

admin.site.register(account.Account, account.AccountAdmin)
admin.site.register(post.PlannedPost, post.PlannedPostAdmin)
admin.site.register(RegularPost)