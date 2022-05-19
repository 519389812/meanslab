from django.contrib import admin
from user.models import CustomUser
from django.contrib.auth.admin import UserAdmin
import json
from django.contrib import messages


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'full_name', 'email')}),
        ('Team', {'fields': ('team',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'ip_address', 'date_joined')}),
    )
    list_display = ('username', 'last_name', 'first_name', 'last_login', 'is_active')
    filter_horizontal = ('groups', 'user_permissions', )
    readonly_fields = ('full_name', )


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.site_header = '后台管理'
admin.site.site_title = '后台管理'
admin.site.index_title = '后台管理'
