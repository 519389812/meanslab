from django.contrib import admin
from industry.models import Industry


class IndustryAdmin(admin.ModelAdmin):
    fields = ('id', 'name')
    list_display = ('id', )


admin.site.register(Industry, IndustryAdmin)
