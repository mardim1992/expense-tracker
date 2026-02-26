from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("expenses/add/", views.add_expense, name="add_expense"),
    path("incomes/add/", views.add_income, name="add_income"),
    path("budget/set/", views.set_budget, name="set_budget"),
    path("register/", views.register_view, name="register"),
]
