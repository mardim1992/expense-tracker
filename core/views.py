from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, RegisterForm, IncomeForm, BudgetForm
from django.db.models import Sum
from datetime import date
from .models import Expense, Income, Budget
from django.core.paginator import Paginator

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

    expenses_qs = Expense.objects.filter(user=request.user, date__gte=month_start, date__lte=today)
    incomes_qs = Income.objects.filter(user=request.user, date__gte=month_start, date__lte=today)

    total_expenses = expenses_qs.aggregate(s=Sum("amount"))["s"] or 0
    total_income = incomes_qs.aggregate(s=Sum("amount"))["s"] or 0
    net = total_income - total_expenses

    budget = Budget.objects.filter(user=request.user, month=month_start).first()
    budget_limit = budget.limit if budget else None
    budget_remaining = (budget_limit - total_expenses) if budget_limit is not None else None

    recent_expenses = Expense.objects.filter(user=request.user).order_by("-date", "-id")[:5]
    recent_incomes = Income.objects.filter(user=request.user).order_by("-date", "-id")[:5]

    context = {
        "month_start": month_start,
        "total_expenses": total_expenses,
        "total_income": total_income,
        "net": net,
        "budget_limit": budget_limit,
        "budget_remaining": budget_remaining,
        "recent_expenses": recent_expenses,
        "recent_incomes": recent_incomes,
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

