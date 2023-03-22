from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("appointment", views.appointment, name="appointment"),
    path("services", views.services, name="services"),
    path("team", views.team, name="team"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path('logout',views.logout,name="logout"),
]
