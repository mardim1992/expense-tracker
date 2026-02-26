from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.db.models import Sum
from datetime import date
from .models import Expense, Income, Budget

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

