from django.contrib import admin

# Register your models here.
from .models import SeekersInstitutes, Wishes, Speeches, WishStatus, SpeechStatus, SocialMedia, CompletionDetails

admin.site.register(SocialMedia)
admin.site.register(Speeches)
admin.site.register(Wishes)
admin.site.register(SeekersInstitutes)
admin.site.register(WishStatus)
admin.site.register(SpeechStatus)
admin.site.register(CompletionDetails)