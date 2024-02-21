from django.contrib import admin
from .models import User, Register, Visualization
import random
from django.core.mail import send_mail
from django.conf import settings  # Import the settings module
from .forms import UserAdminForm
from django.urls import path
from .views import visualization_plot_view

class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    readonly_fields = ['age_group', 'gender', 'movies_per_month']

    def has_change_permission(self, request, obj=None):
            # No one can edit User objects
            return False
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new user, not changing an existing one
            obj.otp = str(random.randint(100000, 999999))  # Generate a random 6-digit OTP
            send_email(obj.email, obj.otp)
        super().save_model(request, obj, form, change)
        
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('analytics/', self.admin_site.admin_view(visualization_plot_view), name="analytics"),
        ]
        return my_urls + urls

def send_email(to_email, otp):
    subject = 'Your OTP'
    message = f'You have been invited to participate in the Neuro Cinematics beta experiment: https://reaimagineapps.pythonanywhere.com/\nTo login, your automatically generated password is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [to_email]
    send_mail(subject, message, email_from, recipient_list)
    
admin.site.register(User, UserAdmin)