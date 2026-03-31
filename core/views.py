from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, RegisterForm, IncomeForm, BudgetForm
from django.db.models import Sum
from datetime import date
from .models import Expense, Income, Budget
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font

def home(request):
    return render(request, "core/home.html")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "core/register.html", {"form": form})

@login_required
def dashboard(request):
    today = date.today()
    month_start = today.replace(day=1)

    expenses_qs = Expense.objects.filter(
        user=request.user,
        date__gte=month_start,
        date__lte=today
    )
    incomes_qs = Income.objects.filter(
        user=request.user,
        date__gte=month_start,
        date__lte=today
    )

    total_expenses = expenses_qs.aggregate(s=Sum("amount"))["s"] or 0
    total_income = incomes_qs.aggregate(s=Sum("amount"))["s"] or 0
    net = total_income - total_expenses

    budget = Budget.objects.filter(user=request.user, month=month_start).first()
    budget_limit = budget.limit if budget else None
    budget_remaining = (budget_limit - total_expenses) if budget_limit is not None else None

    recent_expenses = Expense.objects.filter(user=request.user).order_by("-date", "-id")[:5]
    recent_incomes = Income.objects.filter(user=request.user).order_by("-date", "-id")[:5]

    budget_used_percent = None
    budget_status = None
    budget_message = None

    if budget_limit is not None and budget_limit > 0:
        budget_used_percent = (total_expenses / budget_limit) * 100

        if total_expenses >= budget_limit:
            budget_status = "danger"
            budget_message = "You have exceeded your monthly budget."
        elif budget_used_percent >= 80:
            budget_status = "warning"
            budget_message = "Warning: You have used more than 80% of your monthly budget."
        else:
            budget_status = "safe"
            budget_message = "Good job! Your spending is within the budget."

    context = {
        "month_start": month_start,
        "total_expenses": total_expenses,
        "total_income": total_income,
        "net": net,
        "budget_limit": budget_limit,
        "budget_remaining": budget_remaining,
        "recent_expenses": recent_expenses,
        "recent_incomes": recent_incomes,
        "budget_used_percent": budget_used_percent,
        "budget_status": budget_status,
        "budget_message": budget_message,
    }
    return render(request, "core/dashboard.html", context)

@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect("dashboard")
    else:
        form = ExpenseForm()

    return render(request, "core/add_expense.html", {"form": form})

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            edited_expense = form.save(commit=False)
            edited_expense.user = request.user
            edited_expense.save()
            return redirect("history")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "core/edit_expense.html", {
        "form": form,
        "expense": expense,
    })


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)

    if request.method == "POST":
        expense.delete()
        return redirect("history")

    return render(request, "core/delete_expense.html", {
        "expense": expense,
    })

@login_required
def add_income(request):
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect("dashboard")
    else:
        form = IncomeForm()

    return render(request, "core/add_income.html", {"form": form})
@login_required
def edit_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)

    if request.method == "POST":
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            edited_income = form.save(commit=False)
            edited_income.user = request.user
            edited_income.save()
            return redirect("history")
    else:
        form = IncomeForm(instance=income)

    return render(request, "core/edit_income.html", {
        "form": form,
        "income": income,
    })


@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)

    if request.method == "POST":
        income.delete()
        return redirect("history")

    return render(request, "core/delete_income.html", {
        "income": income,
    })

@login_required
def set_budget(request):
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user

            # normalize month to 1st day
            budget.month = budget.month.replace(day=1)

            # update if already exists
            existing = Budget.objects.filter(user=request.user, month=budget.month).first()
            if existing:
                existing.limit = budget.limit
                existing.save()
            else:
                budget.save()

            return redirect("dashboard")
    else:
        form = BudgetForm()

    return render(request, "core/set_budget.html", {"form": form})
@login_required
def history(request):

    date_from = request.GET.get("from")
    date_to = request.GET.get("to")
    category = request.GET.get("category")

    expenses = Expense.objects.filter(user=request.user).order_by("-date", "-id")
    incomes = Income.objects.filter(user=request.user).order_by("-date", "-id")

    if date_from:
        expenses = expenses.filter(date__gte=date_from)
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
        incomes = incomes.filter(date__lte=date_to)
    if category:
        expenses = expenses.filter(category=category)
        incomes = incomes.filter(category=category)

    exp_paginator = Paginator(expenses, 10)
    inc_paginator = Paginator(incomes, 10)

    exp_page = exp_paginator.get_page(request.GET.get("exp_page"))
    inc_page = inc_paginator.get_page(request.GET.get("inc_page"))

    expense_choices = list(Expense._meta.get_field("category").choices)
    income_choices = list(Income._meta.get_field("category").choices)


    seen = set()
    categories = []
    for value, label in (expense_choices + income_choices):
        if value not in seen:
            categories.append((value, label))
            seen.add(value)

    return render(request, "core/history.html", {
        "exp_page": exp_page,
        "inc_page": inc_page,
        "date_from": date_from or "",
        "date_to": date_to or "",
        "category": category or "",
        "categories":  categories,
    })
@login_required
def reports(request):
    selected_month = request.GET.get("month")

    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)

    if selected_month:
        year, month = selected_month.split("-")
        expenses = expenses.filter(date__year=year, date__month=month)
        incomes = incomes.filter(date__year=year, date__month=month)

    expense_report = (
        expenses.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    income_report = (
        incomes.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    total_expenses = expenses.aggregate(s=Sum("amount"))["s"] or 0
    total_incomes = incomes.aggregate(s=Sum("amount"))["s"] or 0

    
    expense_choices = dict(Expense._meta.get_field("category").choices)
    income_choices = dict(Income._meta.get_field("category").choices)

    for row in expense_report:
        row["label"] = expense_choices.get(row["category"], row["category"])
        row["percent"] = (row["total"] / total_expenses * 100) if total_expenses else 0

    for row in income_report:
        row["label"] = income_choices.get(row["category"], row["category"])
        row["percent"] = (row["total"] / total_incomes * 100) if total_incomes else 0

    return render(request, "core/reports.html", {
        "expense_report": expense_report,
        "income_report": income_report,
        "total_expenses": total_expenses,
        "total_incomes": total_incomes,
        "selected_month": selected_month or "",
    })

@login_required
def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="expense_tracker_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["Type", "Date", "Category", "Amount", "Description"])

    expenses = Expense.objects.filter(user=request.user).order_by("-date", "-id")
    incomes = Income.objects.filter(user=request.user).order_by("-date", "-id")

    for expense in expenses:
        writer.writerow([
            "Expense",
            expense.date,
            expense.get_category_display(),
            expense.amount,
            expense.description,
        ])

    for income in incomes:
        writer.writerow([
            "Income",
            income.date,
            income.get_category_display(),
            income.amount,
            income.description,
        ])

    return response
@login_required
def export_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Expense Tracker Data"

    headers = ["Type", "Date", "Category", "Amount", "Description"]
    worksheet.append(headers)

    
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    expenses = Expense.objects.filter(user=request.user).order_by("-date", "-id")
    incomes = Income.objects.filter(user=request.user).order_by("-date", "-id")

    for expense in expenses:
        worksheet.append([
            "Expense",
            expense.date.strftime("%Y-%m-%d"),
            expense.get_category_display(),
            float(expense.amount),
            expense.description,
        ])

    for income in incomes:
        worksheet.append([
            "Income",
            income.date.strftime("%Y-%m-%d"),
            income.get_category_display(),
            float(income.amount),
            income.description,
        ])

    
    worksheet.column_dimensions["A"].width = 15
    worksheet.column_dimensions["B"].width = 15
    worksheet.column_dimensions["C"].width = 20
    worksheet.column_dimensions["D"].width = 15
    worksheet.column_dimensions["E"].width = 30

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="expense_tracker_data.xlsx"'

    workbook.save(response)
    return response
