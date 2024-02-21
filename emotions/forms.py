from django import forms
from .models import User
from django.conf import settings

class UserVideoForm(forms.Form):
    email = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('email'), 
        required=False,
        label="Email"
    )
    age_group = forms.ChoiceField(
        choices=[('', 'Any Age Group')] + User.AGE_GROUP_CHOICES,
        required=False,
        label="Age Group"
    )
    gender = forms.ChoiceField(
        choices=[('', 'Any Gender')] + User.GENDER_CHOICES,
        required=False,
        label="Gender"
    )
    movies_per_month = forms.ChoiceField(
        choices=[('', 'Any Movies per Month')] + User.MOVIES_PER_MONTH_CHOICES,
        required=False,
        label="Movies per Month"
    )
    video = forms.ChoiceField(
        choices=[(i, v['title']) for i, v in enumerate(settings.VIDEOS)],
        required=True,
        label="Video"
    )


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']  # Only include the email field
