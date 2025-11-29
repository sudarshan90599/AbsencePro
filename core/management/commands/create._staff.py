from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile

MENTORS = [
    ("Bharathi", "bharathi.mca@suranacollege.edu.in", "mentor2024"),
    ("Chandan", "chandan.mca@suranacollege.edu.in", "mentor2024"),
    ("Hemaprabha", "hemaprabha.mca@suranacollege.edu.in", "mentor2024"),
    ("Sujay", "sujay.mca@suranacollege.edu.in", "mentor2024"),
    ("Bhavana", "bhavana.mca@suranacollege.edu.in", "mentor2024"),
    ("Manikantan", "manikantan.mca@suranacollege.edu.in", "mentor2024"),
    ("Naveen", "naveen.mca@suranacollege.edu.in", "mentor2024"),
    ("Priyanka", "priyanka.mca@suranacollege.edu.in", "mentor2024"),
]

DIRECTOR = ("director", "director@suranacollege.edu.in", "director2024")


class Command(BaseCommand):
    help = "Create predefined mentors and director accounts"

    def handle(self, *args, **kwargs):
        for name, email, password in MENTORS:
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(
                    username=email, email=email, password=password, first_name=name.capitalize()
                )
                profile = user.profile
                profile.role = Profile.ROLE_MENTOR
                profile.save()
                self.stdout.write(self.style.SUCCESS(f"Mentor {name} created"))

        d_name, d_email, d_password = DIRECTOR
        if not User.objects.filter(username=d_email).exists():
            user = User.objects.create_user(
                username=d_email, email=d_email, password=d_password, first_name=d_name.capitalize()
            )
            profile = user.profile
            profile.role = Profile.ROLE_DIRECTOR
            profile.save()
            self.stdout.write(self.style.SUCCESS("Director created"))
