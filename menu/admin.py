from django.contrib import admin

from .models import Menu


class MenuItemInline(admin.TabularInline):
    model = Menu
    fk_name = "parent"
    extra = 1


class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]


admin.site.register(Menu, MenuAdmin)
