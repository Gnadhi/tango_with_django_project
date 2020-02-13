from django.contrib import admin
from rango.models import Category, Page, UserProfile


# adds class that will automatically fill the slug field
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "url",)


admin.site.register(Category, CategoryAdmin)  # updates the registration to include this customised interface
admin.site.register(UserProfile)
