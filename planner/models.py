import datetime as dt

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    created = models.DateTimeField(default=dt.datetime.now())

    def __str__(self):
        return self.name


class Todo(models.Model):
    user = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True)
    date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Plan(models.Model):
    user = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.CharField(max_length=200, null=True)
    date = models.DateTimeField(blank=True, null=True)
    start_time = models.TimeField(default=dt.time(00, 00))
    end_time = models.TimeField(default=dt.time(00, 00))
    is_ended = models.BooleanField(default=False)

    def __str__(self):
        return self.plan


class DailyExpense(models.Model):
    user = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    expense_title = models.CharField(max_length=200, null=True)
    type = models.CharField(default="Expense", max_length=200, null=True)
    category = models.CharField(default="Groceries", max_length=200, null=True)
    currency = models.CharField(default="SGD", max_length=100, null=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.expense_title
