# social_connect_app/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.db.models import JSONField

class SeekersInstitutes(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    is_mail_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    phone_no = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True
    )
    is_institute = models.BooleanField(default=False)
    institute_reg_number = models.CharField(max_length=255, blank=True, null=True)
    given_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    institute_details = models.TextField(blank=True, null=True)
    family_name = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    picture = models.URLField(blank=True, null=True)
    locale = models.CharField(max_length=50, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    extra_field = JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_institute:
            if not self.institute_reg_number:
                raise ValueError("Institute registration number is required for institutes.")
            if not self.institute_details:
                raise ValueError("Institute details are required for institutes.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Wishes(models.Model):
    wish_id = models.AutoField(primary_key=True)
    wish_title = models.CharField(max_length=255)
    wish_description = models.TextField()
    created_by = models.ForeignKey(SeekersInstitutes, related_name='wishes_created', on_delete=models.CASCADE)
    is_picked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    category = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    selected_fulfillment = models.ForeignKey('SocialMedia', null=True, blank=True, on_delete=models.SET_NULL, related_name='fulfilled_wish')


    def __str__(self):
        return self.wish_title

class Speeches(models.Model):
    speech_id = models.AutoField(primary_key=True)
    speech_title = models.CharField(max_length=255)
    speech_description = models.TextField()
    created_by = models.ForeignKey(SeekersInstitutes, related_name='speeches_created', on_delete=models.CASCADE)
    is_picked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    category = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    platform_url = models.URLField(blank=True, null=True)
    selected_fulfillment = models.ForeignKey('SocialMedia', null=True, blank=True, on_delete=models.SET_NULL, related_name='fulfilled_speech')


    def __str__(self):
        return self.speech_title


    



class WishStatus(models.Model):
    wish = models.OneToOneField(Wishes, on_delete=models.CASCADE, related_name='wish_status')
    status = models.CharField(max_length=50, default='Created')
    picked_by = models.ManyToManyField(SeekersInstitutes, related_name='picked_wish_statuses', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    

class SpeechStatus(models.Model):
    speech = models.OneToOneField(Speeches, on_delete=models.CASCADE, related_name='speech_status')
    status = models.CharField(max_length=50, default='Created')
    picked_by = models.ManyToManyField(SeekersInstitutes, related_name='picked_speech_statuses', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Speech {self.speech.speech_id} - Status: {self.status}"
    


class SocialMedia(models.Model):
    social_media_id = models.AutoField(primary_key=True)
    wish = models.ForeignKey(Wishes, related_name='social_media_posts', on_delete=models.CASCADE, null=True, blank=True)
    speech = models.ForeignKey(Speeches, related_name='social_media_posts', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(SeekersInstitutes, related_name='social_media_posts', on_delete=models.CASCADE, null=True, blank=True)
    url = JSONField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    platform = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"SocialMedia-{self.social_media_id}"