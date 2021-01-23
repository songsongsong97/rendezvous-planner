from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from .forms import *
import datetime
from pytz import timezone
import pandas as pd
import math
import json
from calendar import monthrange
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count

MONTHS = {1:"January",2:"February",3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October",11:"November",12:"December"}
CURRENCY = ['SGD','MYR']
CATEGORY_CHOICES = ['Car','Charity','Clothing', 'Entertainment', 'Food', 'Groceries', 'Hobbies', 'Incidentials', 'Medical', 'Rent', 'Personal Care', 'Pets', 'School','Utilities', 'Vacation', 'Work']

# Create your views here.
def calendarByMonth(month,year):
    num_days = monthrange(year, month)[1]
    weekday_of_firstday = datetime.date(year, month, 1).weekday()
    days_of_month = [
        {'year': str(year),
         'month': str(month),
         'day': str(day),
         'weekday': str(datetime.date(year, month, day).weekday()),
         }
        for day in range(1, num_days + 1)
    ]
    position_in_calendar = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 0
    }
    position_of_first_day_in_calendar = position_in_calendar[weekday_of_firstday]
    number_of_days_in_first_week = 7 - position_of_first_day_in_calendar
    all_weeks = {}
    # first week
    all_weeks[0] = [{'year':' ', 'month':' ','day':' '}] * position_of_first_day_in_calendar + days_of_month[0:number_of_days_in_first_week]
    days_left = days_of_month[number_of_days_in_first_week::]
    for index in range(len(days_left)):
        row_num = math.floor(index/7) + 1
        if row_num not in all_weeks:
            all_weeks[row_num] = [days_left[index]]
        else:
            all_weeks[row_num].append(days_left[index])
    last_week = all_weeks[len(all_weeks) -1]
    last_week += [{'year':' ', 'month':' ','day':' '}] * (7 - len(last_week))
    # all_weeks = first_week + other_weeks
    context = {'all_weeks': all_weeks, 'currentMonthStr': f"{MONTHS[month]}", 'currentMonth': str(month), 'currentYear': str(year)}
    return context

def calendar(request):
    today = datetime.datetime.now()
    current_month = today.month
    current_year = today.year
    dates_with_plan = []
    if request.user.is_anonymous == False:
        user = request.user.member
        query = Plan.objects.all().filter(user=user,date__month=current_month,date__year=current_year).values('date').annotate(plans=Count('plan'))
        query = list(query)
        dates_with_plan = [str(q['date'].astimezone(timezone('Asia/Kuala_Lumpur')).day) for q in query]
    context = calendarByMonth(current_month,current_year)
    context['dates_with_plan'] = dates_with_plan
    return render(request, 'planner/calendar.html', context)

def calendarWithSelectedMonth(request, year,month):
    today = datetime.datetime.now()
    current_month = int(month)
    current_year = int(year)
    dates_with_plan = []
    if request.user.is_anonymous == False:
        user = request.user.member
        query = Plan.objects.all().filter(user=user,date__month=current_month,date__year=current_year).values('date').annotate(plans=Count('plan'))
        query = list(query)
        dates_with_plan = [str(q['date'].astimezone(timezone('Asia/Kuala_Lumpur')).day) for q in query]
    context = calendarByMonth(current_month,current_year)
    context['dates_with_plan'] = dates_with_plan
    return render(request, 'planner/calendar.html', context)

def getDate(year, month ,day):
    dateString = f"{day} {MONTHS[int(month)]} {year}"
    todo_form = TodoForm()
    planner_form = PlannerForm()
    daily_expenses_form = DailyExpenseForm()
    context = {'dateString': dateString,'currentDay':day, 'currentMonth':month, 'currentYear':year,'todo_form':todo_form,'planner_form':planner_form,'daily_expenses_form':daily_expenses_form}
    return context

def toDate(request, year, month, day):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login')
    else:
        user = request.user.member
        context = getDate(year, month, day)
        date = datetime.datetime(int(year),int(month),int(day))
        todos = Todo.objects.all().filter(user=user,date=date)
        plans = Plan.objects.all().filter(user=user,date=date)
        daily_expenses = DailyExpense.objects.all().filter(user=user,date=date)
        todo_form = context['todo_form']
        planner_form = context['planner_form']
        daily_expenses_form = context['daily_expenses_form']
        context['todos'] = todos
        context['plans'] = plans
        context['daily_expenses'] = daily_expenses
        total_expenses = {}
        total_income = {}
        for c in CURRENCY:
            expense = DailyExpense.objects.all().filter(user=user,date=date,currency=c,type='Expense').aggregate(Sum('amount'))['amount__sum']
            income = DailyExpense.objects.all().filter(user=user,date=date,currency=c,type='Income').aggregate(Sum('amount'))['amount__sum']
            if expense:
                expense = c + str(round(expense,2))
                total_expenses[c] = expense
            if income:
                income = c + str(round(income,2))
                total_income[c] = income
        context['total_income'] = total_income
        context['total_expenses'] = total_expenses
        if request.method == 'POST':
            if 'todo_submit' in request.POST:
                todo_form = TodoForm(request.POST)
                if todo_form.is_valid():
                    todo_model = todo_form.save(commit=False)
                    todo_model.user = user
                    todo_model.date = date
                    todo_model.save()
            if 'planner_submit' in request.POST:
                planner_form = PlannerForm(request.POST)
                if planner_form.is_valid():
                    planner_model = planner_form.save(commit=False)
                    planner_model.user = user
                    planner_model.date = date
                    planner_model.save()
            if 'expense_submit' in request.POST:
                daily_expenses_form = DailyExpenseForm(request.POST)
                if daily_expenses_form.is_valid():
                    expense_model = daily_expenses_form.save(commit=False)
                    if request.POST['type'] == 'Income':
                        expense_model.category = ''
                    expense_model.user = user
                    expense_model.date = date
                    expense_model.save()
            return HttpResponseRedirect(request.path_info)
        return render(request, 'planner/planner.html', context)


def delete_or_update(request,year,month,day,type,pk):
    context = getDate(year, month, day)
    user = request.user.member
    date = datetime.datetime(int(year),int(month),int(day))
    todos = Todo.objects.all().filter(user=user,date=date)
    todo_form = context['todo_form']
    context['todos'] = todos
    plans = Plan.objects.all().filter(user=user,date=date)
    planner_form = context['planner_form']
    context['plans'] = plans
    daily_expenses = DailyExpense.objects.all().filter(user=user,date=date)
    daily_expenses_form = context['daily_expenses_form']
    context['daily_expenses'] = daily_expenses
    edit_task = None
    edit_plan = None
    edit_expense = None
    if type == 'todo':
        edit_task = Todo.objects.all().filter(user=user,date=date).get(id=pk)
    elif type == 'plan':
        edit_plan = Plan.objects.all().filter(user=user,date=date).get(id=pk)
        planner_form.initial['start_time'] = edit_plan.start_time.strftime("%H:%M")
        planner_form.initial['end_time'] = edit_plan.end_time.strftime("%H:%M")
    elif type == 'expense':
        edit_expense = DailyExpense.objects.all().filter(user=user,date=date).get(id=pk)
        daily_expenses_form.initial['type'] = edit_expense.type
        daily_expenses_form.initial['currency'] = edit_expense.currency
        daily_expenses_form.initial['amount'] = edit_expense.amount
    context['edit_task'] = edit_task
    context['edit_plan'] = edit_plan
    context['edit_expense'] = edit_expense
    if request.method == 'POST':
        if 'delete_task' in request.POST:
            edit_task.delete()
            return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
        if 'delete_plan' in request.POST:
            edit_plan.delete()
            return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
        if 'delete_expense' in request.POST:
            edit_expense.delete()
            return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
        if 'complete_task' in request.POST:
            edit_task.completed = not edit_task.completed
            edit_task.save()
            return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
        if 'complete_plan' in request.POST:
            edit_plan.is_ended = not edit_plan.is_ended
            edit_plan.save()
            return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
    return render(request, 'planner/planner.html', context)

def update(request,year,month,day,pk):
    user = request.user.member
    date = datetime.datetime(int(year),int(month),int(day))
    if request.method == 'POST':
        if 'todo_submit' in request.POST:
            todo = Todo.objects.all().filter(user=user,date=date).get(id=pk)
            todo_form = TodoForm(request.POST, instance = todo)
            if todo_form.is_valid():
                todo_model = todo_form.save(commit=False)
                todo_model.user = user
                todo_model.date = date
                todo_model.save()
                return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
        if 'planner_submit' in request.POST:
            plan = Plan.objects.all().filter(user=user,date=date).get(id=pk)
            planner_form = PlannerForm(request.POST, instance = plan)
            if planner_form.is_valid():
                planner_model = planner_form.save(commit=False)
                planner_model.user = user
                planner_model.date = date
                planner_model.save()
                return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
        if 'expense_submit' in request.POST:
            expense = DailyExpense.objects.all().filter(user=user,date=date).get(id=pk)
            daily_expenses_form = DailyExpenseForm(request.POST, instance = expense)
            if daily_expenses_form.is_valid():
                expense_model = daily_expenses_form.save(commit=False)
                expense_model.user = user
                expense_model.date = date
                expense_model.save()
                return HttpResponseRedirect('/' + year + '/' + month + '/' + day)
    return HttpResponseRedirect('/' + year + '/' + month + '/' + day)

def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username OR password is incorrect')
    context={}
    return render(request, 'planner/login.html', context)

def signup(request):
    if request.method=="POST":
        form = CreateMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            form.save()
            messages.success(request, "Account was created successfully for " + username)
            u1 = User.objects.get(username=username, email=email)
            new_user = Member(user=u1,name=username,created=datetime.datetime.now())
            new_user.save()
            return redirect('/login')
    else:
        form = CreateMemberForm()
    return render(request,'planner/signup.html',{'form':form})

def logoutUser(request):
    logout(request)
    return redirect('/')

def month_summary(user, year, month):
    total_sum = {}
    sum_by_date = {}
    total_expenses = {}
    total_incomes = {}
    for c in CURRENCY:
        expense = DailyExpense.objects.all().filter(user=user,date__month=month,date__year=year,currency=c, type='Expense').values('date','category','expense_title').annotate(total = Sum('amount'))
        expense = list(expense)
        total_expenses[c] = expense
        income = DailyExpense.objects.all().filter(user=user,date__month=month,date__year=year,currency=c, type='Income').values('date','category','expense_title').annotate(total = Sum('amount'))
        income = list(income)
        total_incomes[c] = income

        total_expense= sum([round(s['total'],2) for s in expense])
        total_income= sum([round(s['total'],2) for s in income])
        total_sum[c] = total_income - total_expense

        for e in expense:
            day = e['date'].astimezone(timezone('Asia/Kuala_Lumpur')).day
            if day not in sum_by_date:
                sum_by_date[day] = {
                'SGD': 0,
                'MYR': 0
                }
        for i in income:
            day = i['date'].astimezone(timezone('Asia/Kuala_Lumpur')).day
            if day not in sum_by_date:
                sum_by_date[day] = {
                'SGD': 0,
                'MYR': 0
                }


        for e in expense:
            day = e['date'].astimezone(timezone('Asia/Kuala_Lumpur')).day
            sum_by_date[day][c] = round(e['total'],2) * -1

        for i in income:
            day = i['date'].astimezone(timezone('Asia/Kuala_Lumpur')).day
            if sum_by_date[day][c] != 0:
                sum_by_date[day][c] += round(i['total'],2)
            else:
                sum_by_date[day][c] = round(i['total'],2)

    return total_sum, sum_by_date, total_expenses, total_incomes

def summary(request, year, month):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login')
    else:
        user = request.user.member
        year = int(year)
        month = int(month)
        total_expense_by_category = {
            'SGD':[],
            'MYR':[]
        }
        has_expenses ={'SGD': False, 'MYR':False}
        num_days = monthrange(year,month)[1]
        total_sum, sum_by_date, expense, income = month_summary(user, year, month)
        for c in CURRENCY:
            #pie charts
            for category in CATEGORY_CHOICES:
                expense_by_category = DailyExpense.objects.all().filter(user=user,date__month=month,date__year=year,currency=c, type='Expense',category=category).values('date').annotate(total = Sum('amount'))
                expense_by_category = list(expense_by_category)
                if len(expense_by_category) != 0:
                    has_expenses[c] = True
                total_expense_by_category[c].append([category, float(sum([round(s['total'],2) for s in expense_by_category]))])
        context = {'currentMonthStr': f"{MONTHS[month]}", 'currentMonth': month, 'currentYear': year,'total_sum': total_sum, 'sum_by_date': sum_by_date,'total_expense_by_category_sg':json.dumps(total_expense_by_category['SGD']), 'total_expense_by_category_myr':json.dumps(total_expense_by_category['MYR']), 'has_expenses': has_expenses}
        return render(request,'planner/summary.html', context)

def exportFile(request, year, month):
    if request.user.is_anonymous:
        return HttpResponseRedirect('/login')
    else:
        user = request.user.member
        total_sum, sum_by_date, expenses, incomes = month_summary(user, year, month)
        # total_dates = [datetime.datetime(year,month,date).strftime("%Y/%m/%d") for date in sum_by_date]
        total_dates = []
        total_sgd = []
        total_myr = []
        all_titles = []
        all_categories = []
        types = []
        for c in CURRENCY:
            for expense in expenses[c]:
                day = expense['date'].astimezone(timezone('Asia/Kuala_Lumpur')).strftime("%Y/%m/%d")
                total_dates.append(day)
                all_titles.append(expense['expense_title'])
                all_categories.append(expense['category'])
                types.append('Expense')
                if c == 'SGD':
                    total_sgd.append(round(expense['total'],2) * -1)
                    total_myr.append(0)
                elif c == 'MYR':
                    total_myr.append(round(expense['total'],2) * -1)
                    total_sgd.append(0)
            for income in incomes[c]:
                day = income['date'].astimezone(timezone('Asia/Kuala_Lumpur')).strftime("%Y/%m/%d")
                total_dates.append(day)
                all_titles.append(income['expense_title'])
                all_categories.append('')
                types.append('Income')
                if c == 'SGD':
                    total_sgd.append(round(income['total'],2))
                    total_myr.append(0)
                elif c == 'MYR':
                    total_myr.append(round(income['total'],2))
                    total_sgd.append(0)

        df = pd.DataFrame({'Date': total_dates, 'Title':all_titles, 'Type':types, 'Category': all_categories, 'SGD': total_sgd, 'MYR': total_myr})

        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename={MONTHS[int(month)]}_{year}.csv'

        df.to_csv(path_or_buf=resp, sep=',', index=False)

        return resp
