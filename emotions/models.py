from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    zip = models.CharField(max_length=5, null=True, blank=True)
    
    AGE_GROUP_CHOICES = [
        ('under_18', 'Under 18'),
        ('18_24', '18-24'),
        ('25_34', '25-34'),
        ('35_44', '35-44'),
        ('45_54', '45-54'),
        ('55_plus', '55+'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-Binary'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    MOVIES_PER_MONTH_CHOICES = [
        ('0_1', '0 - 1'),
        ('2_4', '2 - 4'),
        ('5_7', '5 - 7'),
        ('8_10', '8 - 10'),
        ('11_15', '11 - 15'),
        ('16_plus', '16+'),
    ]
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    movies_per_month = models.CharField(max_length=10, choices=MOVIES_PER_MONTH_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.email
    
class Visualization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    video_id = models.IntegerField()
    would_buy = models.BooleanField(default=False)  # Or set your preferred default
    amount_to_buy = models.IntegerField(default=0)
    
class Register(models.Model):
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE)
    playback_timestamp = models.FloatField()
    dominantEmotion = models.CharField(max_length=50)
    emotionIntensity = models.FloatField()
    attention = models.FloatField()
