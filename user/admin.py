from django.contrib import admin
from user.models import User, EmailVerifyRecord, Feedback, Industry, District, Team
from django.contrib.auth.admin import UserAdmin
import json
from django.contrib import messages


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


class EmailVerifyRecordAdmin(admin.ModelAdmin):
    pass


class FeedbackAdmin(admin.ModelAdmin):
    pass


class IndustryAdmin(admin.ModelAdmin):
    fields = ('id', 'name')
    list_display = ('id', )


class DistrictAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'parent')
    list_display = ('id', )


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "related_parent_name", )
    list_display_links = ("name", )
    search_fields = ("name", )
    fields = ("name", "parent", "related_parent", "related_parent_name", )
    readonly_fields = ("related_parent", "related_parent_name", )
    ordering = ('-related_parent',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            try:
                if request.user.team.parent:
                    team_id = request.user.team.parent.id
                else:
                    team_id = request.user.team.id
                qs = eval("qs.filter(related_parent__iregex=r'[^0-9]*%s[^0-9]')" % str(team_id))
            except:
                pass
        return qs

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     kwargs["queryset"] = Team.objects.exclude()
    #     return super(TeamAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_head_parent(self, obj):
        if obj.parent != "":
            head_parent = obj.parent
            while True:
                try:
                    head_parent = head_parent.parent
                except:
                    return head_parent
        else:
            return obj

    def related_parent_name(self, obj):
        related_parent_id_list = json.loads(obj.related_parent)
        related_parent_name = '-->'.join([Team.objects.get(id=id).name for id in related_parent_id_list])
        return related_parent_name
    related_parent_name.short_description = "组织关系"

    def get_branch_name(self, obj):
        return obj.branch.branch_id
    get_branch_name.short_description = "成员"

    def get_related_parent(self, parent_object, related_parent):
        while True:
            try:
                related_parent.insert(0, parent_object.id)
                parent_object = parent_object.parent
            except:
                return related_parent

    def delete_included_related_parent(self, team_id):
        included_related_parent_objects = Team.objects.filter(related_parent__iregex=r'\D%s\D' % str(team_id))
        if included_related_parent_objects.count() > 0:
            for object in included_related_parent_objects:
                related_parent = json.loads(object.related_parent)
                related_parent = related_parent[related_parent.index(team_id):]
                object.related_parent = json.dumps(related_parent)
                object.save()

    def change_included_related_parent(self, team_id, changed_related_parent_list):
        included_related_parent_objects = Team.objects.filter(related_parent__iregex=r'\D%s\D' % str(team_id))
        if included_related_parent_objects.count() > 0:
            for object in included_related_parent_objects:
                related_parent = json.loads(object.related_parent)
                related_parent = related_parent[related_parent.index(team_id) + 1:]
                object.related_parent = json.dumps(changed_related_parent_list + related_parent)
                object.save()

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if not change:
                super().save_model(request, obj, form, change)
                related_parent = [obj.id]
                if form.cleaned_data["parent"]:
                    parent = form.cleaned_data["parent"]
                    related_parent = self.get_related_parent(parent, related_parent)
                obj.related_parent = json.dumps(related_parent)
                super().save_model(request, obj, form, change)
            else:
                if obj.id is not None and obj.parent is not None:
                    if obj.id == obj.parent.id:
                        messages.error(request, "保存失败！%s 的上级部门不可为 %s，请重新设置！" % (obj.name, form.cleaned_data["parent"].name))
                        messages.set_level(request, messages.ERROR)
                        return
                if Team.objects.get(id=obj.id).parent != obj.parent:
                    if not obj.parent:
                        super().save_model(request, obj, form, change)
                        self.delete_included_related_parent(obj.id)
                    else:
                        related_parent = [obj.id]
                        parent = obj.parent
                        related_parent = self.get_related_parent(parent, related_parent)
                        self.change_included_related_parent(obj.id, related_parent)
                        obj.related_parent = json.dumps(related_parent)
                        super().save_model(request, obj, form, change)


admin.site.register(Team, TeamAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(District, DistrictAdmin)

admin.site.site_header = '后台管理'
admin.site.site_title = '后台管理'
admin.site.index_title = '后台管理'
