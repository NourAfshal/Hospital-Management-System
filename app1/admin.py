from django.contrib import admin
from django.core.mail import EmailMessage
from .models import Doctor, Nurse, Patient, Appointment
import requests

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'speciality', 'email', 'phone','image']
    list_editable = ['speciality', 'image']
    actions = ['send_email', 'sms_notifications']

    def sms_notifications(self, request, queryset):
        for doctor in queryset:
            if doctor.phone:
                appointments = Appointment.objects.filter(doctor=doctor)
                if appointments:
                    message = f"Appointment details for Doctor {doctor.name.username}:\n"
                    for appointment in appointments:
                        message += f"Patient: {appointment.patient}\nDate: {appointment.appoint_date}\nTime: {appointment.appoint_time}\n\n"
                    #there's an api code url
                    url = f"code{doctor.phone}&code&msg={message}"
                    response = requests.get(url)

                    if response.status_code == 200:
                        self.message_user(request, f"SMS sent to doctor {doctor.name} successfully!")
                    else:
                        self.message_user(request, f"Failed to send SMS to doctor {doctor.name}. Error: {response.text}")
                else:
                    self.message_user(request, f"No appointments found for doctor {doctor.name}")
            else:
                self.message_user(request, f"No phone number available for doctor {doctor.name}")

    sms_notifications.short_description = 'Send SMS Notifications'

    def send_email(self, request, queryset):
        for doctor in queryset:
            if doctor.email:
                appointments = Appointment.objects.filter(doctor=doctor)
                if appointments.exists():
                    email_subject = 'Appointment Details'
                    email_body = f"Dear Dr. {doctor.name},\n\n"
                    email_body += "Your upcoming appointments:\n\n"
                    for appointment in appointments:
                        email_body += f"Date: {appointment.appoint_date}\n"
                        email_body += f"Time: {appointment.appoint_time}\n"
                        email_body += f"Patient: {appointment.patient}\n"
                        email_body += f"Treatment: {appointment.treatment}\n\n"
                    #there's an email instead of code in from_email
                    email = EmailMessage(email_subject, email_body, from_email='code', to=[doctor.email])
                    email.send()

                    self.message_user(request, f"Email sent to doctor {doctor.name} successfully!")
                else:
                    self.message_user(request, f"No appointments found for doctor {doctor.name}")
            else:
                self.message_user(request, f"No email available for doctor {doctor.name}")

    send_email.short_description = 'Send Email Notifications'


class NurseAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    actions = ['send_sms_notifications']

    def send_sms_notifications(self, request, queryset):
        for nurse in queryset:
            if nurse.phone:
                appointments = Appointment.objects.filter(nurse=nurse)
                if appointments:
                    message = f"Appointment details for Nurse {nurse.name}:\n"
                    for appointment in appointments:
                        message += f"Patient: {appointment.patient}\nDate: {appointment.appoint_date}\nTime: {appointment.appoint_time}\n\n"
                    #there's an api code url
                    url = f"code={nurse.phone}&code&msg={message}"
                    response = requests.get(url)

                    if response.status_code == 200:
                        self.message_user(request, f"SMS sent to nurse {nurse.name} successfully!")
                    else:
                        self.message_user(request, f"Failed to send SMS to nurse {nurse.name}. Error: {response.text}")
                else:
                    self.message_user(request, f"No appointments found for nurse {nurse.name}")
            else:
                self.message_user(request, f"No phone number available for nurse {nurse.name}")

    send_sms_notifications.short_description = 'Send SMS Notifications'


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'nurse', 'patient', 'request', 'appoint_date', 'appoint_time']

    def get_queryset(self, request):
        # Only display appointments for the current user
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # Superusers can see all appointments
            return qs
        elif hasattr(request.user, 'doctor'):
            return qs.filter(doctor=request.user.doctor)
        elif hasattr(request.user, 'nurse'):
            return qs.filter(nurse=request.user.nurse)
        else:
            # Non-doctor users won't see any appointments
            return qs.none()

class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'dob', 'address', 'phone', 'email']
    actions = ['send_notifications', 'send_sms']

    def send_sms(self, request, queryset):
        for patient in queryset:
            if patient.phone:
                appointments = Appointment.objects.filter(patient=patient)
                if appointments.exists():
                    message = "Your upcoming appointments:\n\n"
                    for appointment in appointments:
                        message += f"Date: {appointment.appoint_date}\n"
                        message += f"Time: {appointment.appoint_time}\n"
                        message += f"Doctor: {appointment.doctor}\n"
                        message += f"Treatment: {appointment.treatment}\n\n"
                    #there's an api code url
                    url = f"code={patient.phone}&code&msg={message}"
                    response = requests.get(url)

                    if response.status_code == 200:
                        self.message_user(request, f"SMS sent to patient {patient.name} successfully!")
                    else:
                        self.message_user(request, f"Failed to send SMS to patient {patient.name}. Error: {response.text}")
                else:
                    self.message_user(request, f"No appointments found for patient {patient.name}")
            else:
                self.message_user(request, f"No phone number available for patient {patient.name}")

    send_sms.short_description = 'Send SMS Notifications'


    def send_notifications(self, request, queryset):
        for patient in queryset:
            if patient.email:
                appointments = Appointment.objects.filter(patient=patient)
                if appointments.exists():
                    email_subject = 'Appointment Details'
                    email_body = f"Dear {patient.name.username},\n\n"
                    email_body += "Your upcoming appointments:\n\n"
                    for appointment in appointments:
                        email_body += f"Date: {appointment.appoint_date}\n"
                        email_body += f"Time: {appointment.appoint_time}\n"
                        email_body += f"Doctor: {appointment.doctor}\n"
                        email_body += f"Treatment: {appointment.treatment}\n\n"
                    #there's an email instead of code in from_email
                    email = EmailMessage(email_subject, email_body, from_email='code', to=[patient.email])
                    email.send()

                    self.message_user(request, f"Email sent to patient {patient.name.username} successfully!")
                else:
                    self.message_user(request, f"No appointments found for patient {patient.name.username}")
            else:
                self.message_user(request, f"No email available for patient {patient.name.username}")

    send_notifications.short_description = 'Send Notifications'


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Nurse, NurseAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Patient, PatientAdmin)
