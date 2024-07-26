from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView, View
from .models import Menu


class MenusView(ListView):
    model = Menu
    template_name = "menu/menus.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.template_name)


class MenuView(View):
    model = Menu
    template_name = "menu/menus.html"

    def get(self, request: HttpRequest, name: str):
        context = {"name": name}
        p = request.GET.get("p")
        if p is not None:
            context["selected_path"] = p
        return render(request, self.template_name, context=context)
