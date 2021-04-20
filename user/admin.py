from django.contrib import admin
from user.models import User, EmailVerifyRecord, Feedback
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Team', {'fields': ('team',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'ip_address', 'date_joined')}),
    )
    list_display = ('username', 'last_name', 'first_name', 'last_login', 'is_active')
    filter_horizontal = ('groups', 'user_permissions', )
    # readonly_fields = ('branch_id',)

    # def get_readonly_fields(self, request, obj=None):
    #     if request.user.is_superuser:
    #         readonly_fields = ('team_id',)
    #     else:
    #         readonly_fields = ('team_id', 'team_name')
    #     return readonly_fields

#     def get_branch_name(self, obj):
#         return obj.branch.name
#     get_branch_name.short_description = "团队名"
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.filter(team_id=request.user.branch.branch_id)
#
#     def save_model(self, request, obj, form, change):
#         if form.is_valid():
#             if obj.branch_id is None:
#                 obj.branch_id = request.user.branch.branch_id
#             super().save_model(request, obj, form, change)


class EmailVerifyRecordAdmin(admin.ModelAdmin):
    pass


class FeedbackAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
admin.site.register(Feedback, FeedbackAdmin)

admin.site.site_header = '后台管理'
admin.site.site_title = '后台管理'
admin.site.index_title = '后台管理'
