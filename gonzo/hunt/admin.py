from django.contrib import admin
from gonzo.hunt.models import *

#
# Admin
#
class HuntAdmin(admin.ModelAdmin):
    list_display = ('slug','start_time')
    prepopulated_fields = {"slug":("phrase",)}


admin.site.register(Hunt, HuntAdmin)
admin.site.register(Submission)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Award)
