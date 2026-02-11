from django.db import models
from django.contrib.auth.models import User

# Predefined expense categories (stored value, human label)
EXPENSE_CATEGORIES = [
    ("FOOD", "Food"),
    ("TRANSPORT", "Transport"),
    ("BILLS", "Bills"),
    ("RENT", "Rent"),
    ("HEALTH", "Health"),
    ("ENTERTAINMENT", "Entertainment"),
    ("OTHER", "Other"),
]

# Predefined income categories
INCOME_CATEGORIES = [
    ("SALARY", "Salary"),
    ("FREELANCE", "Freelance"),
    ("RENT_INCOME", "Rent Income"),
    ("GIFT", "Gift"),
    ("OTHER", "Other"),
]


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=30, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_category_display()} - {self.amount}"


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=30, choices=INCOME_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_category_display()} - {self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # store as first day of month, e.g. 2025-12-01
    limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.month} - {self.limit}"


