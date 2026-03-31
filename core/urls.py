from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("expenses/add/", views.add_expense, name="add_expense"),
    path("expenses/<int:expense_id>/edit/", views.edit_expense, name="edit_expense"),
    path("expenses/<int:expense_id>/delete/", views.delete_expense, name="delete_expense"),
    path("incomes/add/", views.add_income, name="add_income"),
     path("incomes/<int:income_id>/edit/", views.edit_income, name="edit_income"),
    path("incomes/<int:income_id>/delete/", views.delete_income, name="delete_income"),
    path("incomes/<int:income_id>/edit/", views.edit_income, name="edit_income"),
    path("incomes/<int:income_id>/delete/", views.delete_income, name="delete_income"),
    path("budget/set/", views.set_budget, name="set_budget"),
    path("history/", views.history, name="history"),
    path("reports/", views.reports, name="reports"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("export/excel/", views.export_excel, name="export_excel"),
    path("register/", views.register_view, name="register"),
]
