from django.urls import path, include
from .views import MenusView, MenuView

urlpatterns = [
    path("", MenusView.as_view(), name="index"),
    path("<str:name>/", MenuView.as_view()),
]
