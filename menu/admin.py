from django.contrib import admin

from .models import Menu


class MenuItemInline(admin.TabularInline):
    model = Menu
    fk_name = "parent"
    extra = 1
    show_change_link = True


class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
    list_filter = ("parent",)
    ordering = ("name", "id")
    list_display = ("id", "name")


admin.site.register(Menu, MenuAdmin)
