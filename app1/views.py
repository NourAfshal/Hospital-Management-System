from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView
from django.utils import timezone
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django import forms
import uuid
import requests
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Nurse, Appointment, Doctor

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            if hasattr(request.user, 'doctor'):
                return redirect('doctor')
            elif hasattr(request.user, 'nurse'):
                return redirect('nurse')
            return redirect('appointment')
        else:
            form = AuthenticationForm()
            return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if hasattr(request.user, 'doctor'):
                return redirect('doctor')
            elif hasattr(request.user, 'nurse'):
                return redirect('nurse')
            return redirect('appointment')

        return render(request, self.template_name, {'form': form})


class AppointmentTemplateView(TemplateView):
    template_name = 'patient_register.html'

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        dob = request.POST.get("dob")
        password = request.POST.get("password") # Assuming the date of birth input field name is "dob" in the form

        # Retrieve or create the corresponding User instance
        user, _ = User.objects.get_or_create(username=name)
        user.set_password(password)
        user.save()

        # Create a new patient object
        patient = Patient(
            name=user,
            email=email,
            phone=mobile,
            address=address,
            dob=dob,  # Assign the provided date of birth to the "dob" attribute
        )
        patient.save()

        return HttpResponseRedirect(reverse('appointment'))


class DoctorTemplateView(TemplateView):
    template_name = 'doctor_register.html'

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        speciality = request.POST.get("speciality")
        password = request.POST.get("password")# Assuming the speciality input field name is "speciality" in the form
        image = request.FILES.get("image")

        # Retrieve or create the corresponding User instance
        user, _ = User.objects.get_or_create(username=name)
        user.set_password(password)
        user.save()

        if image:
            filename = image.name
            path = default_storage.save(filename, ContentFile(image.read()))
        else:
            path = 'user.jpg'  # Set a default image path if no image is provided

        # Create a new doctor object
        doctor = Doctor(
            name=user,
            speciality=speciality,
            email=email,
            phone=mobile,
            image=path,
        )
        doctor.save()

        return HttpResponseRedirect(reverse('doctor'))


class NurseTemplateView(TemplateView):
    template_name = 'nurse_register.html'

    def post(self, request):
        name = request.POST.get("name")
        password = request.POST.get("password")
        mobile = request.POST.get("mobile")

        # Create or retrieve the User instance
        user, _ = User.objects.get_or_create(username=name)
        user.set_password(password)
        user.save()

        # Create a new nurse object
        nurse = Nurse(
            name=user,
            phone=mobile,
        )
        nurse.save()

        return HttpResponseRedirect(reverse('nurse'))

class ManageAppointmentTemplateView(TemplateView):
    template_name = "appointment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['doctors'] = Doctor.objects.all()
        return context

    def post(self, request):
        doctor_name = request.POST.get("doctor")  # Retrieve doctor name from the form data

        # Retrieve the User instance associated with the provided doctor name
        doctor_user = User.objects.get(username=doctor_name)

        # Retrieve the Doctor instance based on the User instance
        doctor = Doctor.objects.get(name=doctor_user)

        nurses = Nurse.objects.all()
        nurse = random.choice(nurses)  # Choose a random Nurse instance

        patient_name = request.POST.get("name")  # Retrieve patient name from the form data

        # Retrieve the User instance associated with the provided patient name
        patient_user = User.objects.get(username=patient_name)

        # Retrieve the Patient instance based on the User instance
        patient = Patient.objects.get(name=patient_user)

        message = request.POST.get("message")
        appoint_date = request.POST.get("date")
        appoint_time = request.POST.get("time")

        appointment = Appointment(
            patient=patient,
            doctor=doctor,
            nurse=nurse,  # Assign the Nurse instance
            request=message,
            appoint_date=appoint_date,
            appoint_time=appoint_time,
        )
        appointment.save()

        send_mail(
            f'Appointment Details for the Patient {patient.name}',
            f'An appointment request has been submitted for {patient.name} with Dr {doctor.name}.\nDate: {appointment.appoint_date}\nTime: {appointment.appoint_time}\n\nStay Safe\nMedicio Hospital.',
            settings.EMAIL_HOST_USER,  # Sender's email address
            [patient.email],  # List of recipient email addresses
            fail_silently=False,
        )
        return render(request, self.template_name)


@login_required(login_url='login')
def doctor(request):
    doctor = Doctor.objects.get(name=request.user)
    nurses = Nurse.objects.all()
    appointments = Appointment.objects.filter(doctor=doctor)

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        patient_name = request.POST.get('patientName')
        appoint_time = request.POST.get('appointTime')
        appoint_date = request.POST.get('appointDate')
        nurse_name = request.POST.get('nurseName')
        request_text = request.POST.get('request')

        # Get the appointment object
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Update the appointment details
        appointment.patient.name.username = patient_name
        appointment.appoint_time = appoint_time
        appointment.appoint_date = appoint_date
        appointment.nurse.name.username = nurse_name
        appointment.request = request_text

        # Save the related objects
        appointment.patient.save()
        appointment.nurse.save()
        appointment.save()

        # Update the appointments queryset with the saved appointment
        appointments = Appointment.objects.filter(doctor=doctor)

    context = {
        'doctor': doctor,
        'nurses': nurses,
        'appointments': appointments,
    }
    return render(request, 'doctor.html', context)




@login_required(login_url='login')
def nurse(request):
    nurse = Nurse.objects.get(name=request.user)
    appointments = Appointment.objects.filter(nurse=nurse)
    doctors = Doctor.objects.all()

    context = {
        'nurse': nurse,
        'appointments': appointments,
        'doctors': doctors,
    }
    return render(request, 'nurse.html', context)

@csrf_exempt
def delete_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)

        # Check if the logged-in nurse is assigned to the appointment
        if appointment.nurse.name == request.user.username:
            appointment.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Appointment not found'})


def home(request):
    doctors = Doctor.objects.all()
    context = {
        'doctors': doctors,
    }
    return render(request, 'index.html', context)

@login_required(login_url='login')
def appointment(request):
    return render(request, 'appointment.html')


def send_appointment_reminder():
    # Get today's date
    today = datetime.now().date()

    # Calculate the date for one day from now
    one_day_from_now = today + timedelta(days=1)

    # Retrieve appointments scheduled for one day from now
    appointments = Appointment.objects.filter(appoint_date=one_day_from_now)

    # Iterate over the appointments
    for appointment in appointments:
        doctor = appointment.doctor
        patient = appointment.patient

        # Prepare the email content
        subject = f'Appointment Reminder: {patient.name} - {appointment.appoint_date}'
        email_body = f"Dear Dr. {doctor.name},\n\n"
        email_body += "Your upcoming appointments:\n\n"
        for appointment in appointments:
            email_body += f"Date: {appointment.appoint_date}\n"
            email_body += f"Time: {appointment.appoint_time}\n"
            email_body += f"Patient: {appointment.patient}\n"
            email_body += f"Treatment: {appointment.treatment}\n\n"
        from_email = settings.EMAIL_HOST_USER

        # Send the email
        email = EmailMessage(subject, email_body, from_email, to=[doctor.email])
        email.send()



