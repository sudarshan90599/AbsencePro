# core/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile, LeaveRequest
from django.core.exceptions import ValidationError
import re

class StudentRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Full Name")
    email = forms.EmailField(label="College Email")
    mobile = forms.CharField(max_length=15, label="Mobile Number")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        pattern = r'^[a-zA-Z0-9]+\.mca23@suranacollege\.edu\.in$'
        if not re.match(pattern, email):
            raise ValidationError("College email must be in the format 'studentname.mca23@suranacollege.edu.in'")
        if User.objects.filter(username=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile'].strip()
        if not mobile.isdigit() or len(mobile) != 10:
            raise ValidationError("Mobile number should be exactly 10 digits.")
        return mobile
    
    def clean_password(self):
        pw = self.cleaned_data.get("password", "")
        if len(pw) <= 6:
            raise ValidationError("Password must be longer than 6 characters.")
        if not re.search(r'[A-Z]', pw):
            raise ValidationError("Password must contain at least one uppercase letter.")
        return pw

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        cpw = cleaned.get("confirm_password")
        if pw and cpw and pw != cpw:
            self.add_error("confirm_password", "Password doesn't match.")


class LoginForm(forms.Form):
    email = forms.EmailField(label="College Email")
    password = forms.CharField(widget=forms.PasswordInput)


class StaffLoginForm(forms.Form):
    role = forms.ChoiceField(choices=[('MENTOR', 'Mentor'), ('DIRECTOR', 'Director')])
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dob', 'ussn', 'semester', 'year', 'course', 'specialization']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'ussn': forms.TextInput(attrs={'placeholder': 'Enter your USSN'}),
            'semester': forms.TextInput(attrs={'placeholder': 'Enter your semester'}),
            'year': forms.TextInput(attrs={'placeholder': 'Year'}),
            'course': forms.TextInput(attrs={'placeholder': 'Course'}),
            'specialization': forms.TextInput(attrs={'placeholder': 'Specialization'}),
        }

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'mentor']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict mentor dropdown ONLY to mentors you created
        allowed_mentors = [
            "bharathi.mca@suranacollege.edu.in",
            "chandan.mca@suranacollege.edu.in",
            "hemaprabha.mca@suranacollege.edu.in",
            "sujay.mca@suranacollege.edu.in",
            "bhavana.mca@suranacollege.edu.in",
            "manikantan.mca@suranacollege.edu.in",
            "naveen.mca@suranacollege.edu.in",
            "priyanka.mca@suranacollege.edu.in"
        ]
        self.fields['mentor'].queryset = User.objects.filter(
            profile__role=Profile.ROLE_MENTOR,
            email__in=allowed_mentors
        )
        self.fields['mentor'].label_from_instance = lambda obj: obj.first_name.capitalize()


    def clean_reason(self):
        reason = self.cleaned_data.get("reason", "")
        if len(reason.strip()) < 10:
            raise ValidationError("Reason must be at least 10 characters long.")
        return reason

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        mentor = cleaned_data.get("mentor")

        if start and end:
            duration_days = (end - start).days + 1

            if duration_days <= 2:
                if not mentor:
                    raise ValidationError("For leave ≤ 2 days, you must select a mentor.")
            else:
                if mentor:
                    raise ValidationError("For leave > 2 days, mentor should not be selected (goes to director).")

        return cleaned_data
