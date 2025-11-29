# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    #  Main pages
    path("", views.index, name="index"),
    path("dashboard/", views.main_dashboard, name="main_dashboard"), 

    #  Student authentication & dashboard
    path("student/signin/", views.student_signin, name="student_signin"),
    path("student/register/", views.student_register, name="student_register"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/profile/edit/", views.edit_profile, name="edit_profile"),
    path("student/leave/request/", views.request_leave, name="request_leave"),

    #  Staff authentication
    path("staff/signin/", views.staff_signin, name="staff_signin"),
    path("mentor/dashboard/", views.mentor_dashboard, name="mentor_dashboard"),
    path("director/dashboard/", views.director_dashboard, name="director_dashboard"),

    #  Leave review (mentor/director)
    path("leave/<int:pk>/review/", views.review_leave, name="review_leave"),

    # Logout
    path("logout/", views.logout_view, name="logout"),
]
