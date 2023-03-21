from django.urls import path

from .views import (
    calendar,
    calendar_with_selected_month,
    delete_or_update,
    export_file,
    login_user,
    logout_user,
    signup,
    summary,
    to_date,
    update_obj,
)

urlpatterns = [
    path("", calendar, name="calendar"),
    path("<str:year>/<str:month>/<str:day>/", to_date, name="date"),
    path(
        "<str:year>/<str:month>/<str:day>/update/<str:pk>/", update_obj, name="update"
    ),
    path(
        "<str:year>/<str:month>/<str:day>/edit/<str:type>/<str:pk>/",
        delete_or_update,
        name="delete_or_update",
    ),
    path(
        "<str:year>/<str:month>/",
        calendar_with_selected_month,
        name="calendar_by_month",
    ),
    path("<str:year>/<str:month>/summary", summary, name="summary"),
    path("login/", login_user, name="login"),
    path("signup/", signup, name="signup"),
    path("logout/", logout_user, name="logout"),
    path("<str:year>/<str:month>/summary/download", export_file, name="export_file"),
]
