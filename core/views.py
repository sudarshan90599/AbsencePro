# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, LoginForm, ProfileForm, LeaveRequestForm, StaffLoginForm
from django.contrib.auth.models import User
from .models import Profile, LeaveRequest
from django.contrib import messages
from django.utils import timezone

def index(request):
    return render(request, "core/index.html")


def student_signin(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            pwd = form.cleaned_data['password']
            user = authenticate(request, username=email, password=pwd)
            if user and hasattr(user, 'profile') and user.profile.role == Profile.ROLE_STUDENT:
                login(request, user)
                return redirect('student_dashboard')
            messages.error(request, "Invalid student credentials.")
    else:
        form = LoginForm()
    return render(request, "core/student_signin.html", {"form": form})


def staff_signin(request):
    if request.method == "POST":
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            email = form.cleaned_data['email'].lower()
            pwd = form.cleaned_data['password']
            user = authenticate(request, username=email, password=pwd)
            if user and hasattr(user, 'profile') and user.profile.role == role:
                login(request, user)
                if role == Profile.ROLE_MENTOR:
                    return redirect('mentor_dashboard')
                elif role == Profile.ROLE_DIRECTOR:
                    return redirect('director_dashboard')
            messages.error(request, "Invalid staff credentials or wrong role selected.")
    else:
        form = StaffLoginForm()
    return render(request, "core/staff_signin.html", {"form": form})


def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            full_name = form.cleaned_data['full_name']
            mobile = form.cleaned_data['mobile']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
            profile = user.profile
            profile.phone = mobile
            profile.role = Profile.ROLE_STUDENT
            profile.save()

            login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect('student_dashboard')
        
    else:
        form = StudentRegistrationForm()
    return render(request, "core/student_register.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def student_dashboard(request):
    if request.user.profile.role != Profile.ROLE_STUDENT:
        return redirect('index')
    profile = request.user.profile
    leaves = request.user.leaves.order_by('-created_at')[:10]
    stats = {
        "pending": request.user.leaves.filter(status=LeaveRequest.STATUS_PENDING).count(),
        "approved": request.user.leaves.filter(status=LeaveRequest.STATUS_APPROVED).count(),
        "rejected": request.user.leaves.filter(status=LeaveRequest.STATUS_REJECTED).count(),
    }
    return render(request, "core/student_dashboard.html", {"profile": profile, "leaves": leaves, "stats": stats})


@login_required
def edit_profile(request):
    if request.user.profile.role != Profile.ROLE_STUDENT:
        return redirect('index')
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('student_dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/edit_profile.html", {"form": form, "profile": profile})


@login_required
def request_leave(request):
    if request.user.profile.role != Profile.ROLE_STUDENT:
        return redirect('index')

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            lr = form.save(commit=False)
            lr.student = request.user

            # Calculate duration
            duration = (lr.end_date - lr.start_date).days + 1

            if duration > 2:
                # Route directly to Director
                lr.mentor = None
                director_profile = Profile.objects.filter(role=Profile.ROLE_DIRECTOR).first()
                if director_profile:
                    lr.approver = director_profile.user
            else:
                # Assign to selected Mentor
                if lr.mentor:
                    lr.approver = lr.mentor

            lr.save()
            messages.success(request, "Leave request submitted.")
            return redirect('student_dashboard')
    else:
        form = LeaveRequestForm()

    mentors = User.objects.filter(profile__role=Profile.ROLE_MENTOR)
    return render(request, "core/request_leave.html", {"form": form, "mentors": mentors})




def mentor_dashboard(request):
    if request.user.profile.role != Profile.ROLE_MENTOR:
        return redirect('index')

    pending = LeaveRequest.objects.filter(
        approver=request.user,
        status=LeaveRequest.STATUS_PENDING
    ).order_by('-created_at')

    approved = LeaveRequest.objects.filter(
        approver=request.user,
        status=LeaveRequest.STATUS_APPROVED
    ).order_by('-reviewed_at')

    rejected = LeaveRequest.objects.filter(
        approver=request.user,
        status=LeaveRequest.STATUS_REJECTED
    ).order_by('-reviewed_at')

    stats = {
        "pending": pending.count(),
        "approved": approved.count(),
        "rejected": rejected.count(),
    }

    return render(request, "core/mentor_dashboard.html", {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "stats": stats,
    })



def director_dashboard(request):
    if request.user.profile.role != Profile.ROLE_DIRECTOR:
        return redirect('index')

    pending = LeaveRequest.objects.filter(
        approver=request.user,
        status=LeaveRequest.STATUS_PENDING
    ).order_by('-created_at')

    approved = LeaveRequest.objects.filter(
        approver=request.user,
        status=LeaveRequest.STATUS_APPROVED
    ).order_by('-reviewed_at')

    rejected = LeaveRequest.objects.filter(
        approver=request.user,
        status=LeaveRequest.STATUS_REJECTED
    ).order_by('-reviewed_at')

    stats = {
        "pending": pending.count(),
        "approved": approved.count(),
        "rejected": rejected.count(),
    }

    return render(
        request,
        "core/director_dashboard.html",
        {"pending": pending, "approved": approved, "rejected": rejected, "stats": stats}
    )


@login_required
def review_leave(request, pk):
    lr = get_object_or_404(LeaveRequest, pk=pk)
    if request.user != lr.approver:
        messages.error(request, "You are not authorized to review this request.")
        return redirect('index')

    if request.method == "POST":
        action = request.POST.get("action")
        comments = request.POST.get("comments", "").strip()
        if action == "approve":
            lr.status = LeaveRequest.STATUS_APPROVED
            lr.review_comments = comments
            lr.reviewed_at = timezone.now()
            lr.save()
            messages.success(request, "Leave approved.")
        elif action == "reject":
            lr.status = LeaveRequest.STATUS_REJECTED
            lr.review_comments = comments
            lr.reviewed_at = timezone.now()
            lr.save()
            messages.success(request, "Leave rejected.")
        return redirect('mentor_dashboard' if request.user.profile.role == Profile.ROLE_MENTOR else 'director_dashboard')

    return render(request, "core/review_leave.html", {"lr": lr})



def main_dashboard(request):
    return render(request, "core/main_dashboard.html")