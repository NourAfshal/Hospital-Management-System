from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Doctor(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.IntegerField()
    image = models.ImageField(upload_to='media/', default='user.jpg')

    def __str__(self):
        return self.name.username

class Nurse (models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.IntegerField()

    def __str__(self):
        return self.name.username

class Patient(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    address = models.CharField(max_length=200, null=False, blank=False)
    phone = models.IntegerField()
    email = models.EmailField(null=True, blank=True)

    @property
    def get_age(self):
        return relativedelta(datetime.now(), self.dob).years

    def __str__(self):
        return f"{self.name.username}: {self.get_age} years old"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    appoint_date = models.DateField(null=False, blank=False)
    appoint_time = models.TimeField(null=False, blank=False)
    request = models.TextField(blank=True)

    def __str__(self):
        return f"Appointment with doctor {self.doctor.name.username} on {self.appoint_date} at {self.appoint_time}"
