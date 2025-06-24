from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('public', 'Public'),
        ('police', 'Police'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username




class PoliceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    station = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} - {self.station}"


class CrimeReport(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)  # username link
    name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=15)
    email = models.EmailField()
    description = models.TextField()

    # Crime Location
    crime_location = models.CharField(max_length=255)
    crime_date = models.DateField()
    crime_time = models.TimeField()

    # Home Address
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    village = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)

    # Evidence
    evidence_file = models.FileField(upload_to='evidence/', blank=True, null=True)

    # Status & Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    investigation_notes = models.TextField(blank=True, null=True)

    # Timestamp
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class ContactUsComplaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=15)
    email = models.EmailField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    village = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    complaint = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.name} - {self.status()}"