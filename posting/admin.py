from django.contrib import admin

from posting.accounts import account
from .models import ManualPost, RegularPost

admin.site.register(account.Account, account.AccountAdmin)
admin.site.register(ManualPost)
admin.site.register(RegularPost)