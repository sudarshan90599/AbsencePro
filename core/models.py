# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_STUDENT = "STUDENT"
    ROLE_MENTOR = "MENTOR"
    ROLE_DIRECTOR = "DIRECTOR"
    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_MENTOR, "Mentor"),
        (ROLE_DIRECTOR, "Director"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    phone = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    ussn = models.CharField(max_length=50, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    year = models.CharField(max_length=10, blank=True)
    course = models.CharField(max_length=10, blank=True)
    specialization = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class LeaveRequest(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    LEAVE_PERSONAL = "Personal Leave"
    LEAVE_SICK = "Sick Leave"
    LEAVE_OTHER = "Other"
    LEAVE_CHOICES = [
        (LEAVE_PERSONAL, "Personal Leave"),
        (LEAVE_SICK, "Sick Leave"),
        (LEAVE_OTHER, "Other"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leaves")
    leave_type = models.CharField(max_length=40, choices=LEAVE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    mentor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_leaves")
    approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_leaves")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    review_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    @property
    def num_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"Leave {self.pk} by {self.student.username} ({self.status})"
 