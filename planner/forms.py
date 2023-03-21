import datetime as dt

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DailyExpense, Plan, Todo

HOUR_CHOICES = [(dt.time(hour=x), "{:02d}:00".format(x)) for x in range(0, 24)]


class TodoForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Add new task ..."})
    )

    class Meta:
        model = Todo
        fields = "__all__"


class PlannerForm(forms.ModelForm):
    plan = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Add new plan ..."})
    )
    start_time = forms.DateTimeField(
        required=True,
        input_formats=["%H:%M"],
        localize=True,
        widget=forms.DateInput(attrs={"placeholder": "HH:MM"}),
    )
    end_time = forms.DateTimeField(
        required=True,
        input_formats=["%H:%M"],
        localize=True,
        widget=forms.DateInput(attrs={"placeholder": "HH:MM"}),
    )

    class Meta:
        model = Plan
        fields = "__all__"

    # Logic for raising error if end_time < start_time
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if end_time < start_time:
            raise forms.ValidationError("End time should be greater than start time.")
        return super().clean()


class DailyExpenseForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ("Car", "Car"),
        ("Charity", "Charity"),
        ("Clothing", "Clothing"),
        ("Entertainment", "Entertainment"),
        ("Food", "Food"),
        ("Groceries", "Groceries"),
        ("Hobbies", "Hobbies"),
        ("Incidentials", "Incidentials"),
        ("Medical", "Medical"),
        ("Rent", "Rent"),
        ("Personal Care", "Personal Care"),
        ("Pets", "Pets"),
        ("School", "School"),
        ("Utilities", "Utilities"),
        ("Vacation", "Vacation"),
        ("Work", "Work"),
    ]
    TYPE_CHOICES = [("Expense", "Expense"), ("Income", "Income")]
    CURRENCY_CHOICES = [("SGD", "SGD"), ("MYR", "MYR")]
    expense_title = forms.CharField(widget=forms.TextInput())
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={"onchange": "hideCategories();"}),
    )
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    amount = forms.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = DailyExpense
        fields = "__all__"


class CreateMemberForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is not unique")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is not unique")
        return email
