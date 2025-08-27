from django.contrib import admin

from .account import Account, AccountAdmin
from .planned_post import PlannedPost, PlannedPostAdmin
from .regular_post import RegularPost

admin.site.register(Account, AccountAdmin)
admin.site.register(PlannedPost, PlannedPostAdmin)
admin.site.register(RegularPost)