# core/admin.py
from django.contrib import admin
from .models import Profile, LeaveRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone")

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "leave_type", "start_date", "end_date", "status")
    list_filter = ("status", "leave_type")
