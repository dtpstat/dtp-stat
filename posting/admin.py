from django.contrib import admin

from posting.accounts import account
from posting import planned_post
from .models import RegularPost

admin.site.register(account.Account, account.AccountAdmin)
admin.site.register(planned_post.PlannedPost, planned_post.PlannedPostAdmin)
admin.site.register(RegularPost)