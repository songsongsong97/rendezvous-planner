from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar, name="calendar"),
    path('<str:year>/<str:month>/<str:day>/', views.toDate, name='date'),
    path('<str:year>/<str:month>/<str:day>/update/<str:pk>/', views.update, name='update'),
    path('<str:year>/<str:month>/<str:day>/edit/<str:type>/<str:pk>/', views.delete_or_update, name='delete_or_update'),
    path('<str:year>/<str:month>/', views.calendarWithSelectedMonth, name='calendar_by_month'),
    path('<str:year>/<str:month>/summary', views.summary, name='summary'),
    path('login/', views.loginUser,name='login'),
    path('signup/', views.signup,name='signup'),
    path('logout/', views.logoutUser, name='logout'),
    path('<str:year>/<str:month>/summary/download', views.exportFile, name='exportFile'),
]
