# social_connect_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('create-user/', views.create_user, name='create_user'),
    path('create-wish/', views.create_wish, name='create_wish'), 
    path('create-speech/', views.create_speech, name='create_speech'),
    path('pick-wish/', views.pick_wish, name='pick_wish'),
    path('pick-speech/', views.pick_speech, name='pick_speech'), 
    path('wishes/', views.list_wishes, name='list_wishes'),
    path('speeches/', views.list_speeches, name='list_speeches'),
    path('wish-by-category/<str:category>/', views.wish_by_category, name='wish_by_category'),
    path('user-wish/<int:user_id>/', views.user_wishes, name='user_wishes'),
    path('wishes-by-location/', views.wishes_by_location_view, name='wishes_by_location'),
    path('already-user/', views.check_user_exists, name='check_user_exists'),
    path('change-status/', views.change_status, name='change_status'),
    path('categories/', views.get_categories, name='categories'),
    path('wishes/<int:wishID>/', views.get_wish_details, name='wish-details'),
    path('user-speech/<int:userID>/', views.get_user_speeches, name='user-speeches'),
    path('speeches/<int:speechID>/', views.get_speech_details, name='speech-details'),
    path('fulfill/', views.create_social_media_post, name='fulfill'),
    path('event/', views.event, name='event'),
    path('event/<str:event_type>/<int:event_id>/', views.event_by_id, name='event_by_id'),
    path('user/<int:userID>/', views.user_details, name='user_details'),
    path('speech-by-category/<category>/', views.speeches_by_category, name='speeches_by_category'),
    path('speech-by-location/', views.speeches_by_location_view, name='speeches_by_location'),
    path('update-user/<int:user_id>/', views.update_user, name='update_user'),
    path('get-fulfill-details/', views.get_fulfill_details, name='get_fulfill_details'),
    path('get-fulfill-details/<int:socialMediaID>/', views.get_social_media, name='get_social_media'),
    path('get-user-summary/<int:userID>/', views.get_user_summary, name='get-user-summary'),
    path('sign-up-user/', views.sign_up_user_view, name='sign_up_user'),
    path('sign-in-user/', views.sign_in_user_view, name='sign_in_user'),
    path('sign-out/', views.sign_out_view, name='sign_out'),
]