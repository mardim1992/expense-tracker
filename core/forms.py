from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, Income, Budget

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ExpenseForm(forms.ModelForm):  
    class Meta:
        model = Expense
        fields = ["amount", "category", "date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["amount", "category", "date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["month", "limit"]
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
        }

