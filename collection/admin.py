from django.contrib import admin
from collection.models import Classification, Collection, Rate, Recommendation, Comment


class ClassificationAdmin(admin.ModelAdmin):
    pass


class CollectionAdmin(admin.ModelAdmin):
    pass


class RateAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


class RecommendationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
