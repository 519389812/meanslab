from django.contrib import admin
from district.models import District


class DistrictAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'parent')
    list_display = ('id', )


admin.site.register(District, DistrictAdmin)
