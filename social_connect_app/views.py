# social_connect_app/views.py

from django.forms import model_to_dict
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from math import radians, sin, cos, sqrt, atan2
from django.shortcuts import get_object_or_404 
from django.db.models import Q
from .models import SeekersInstitutes, Wishes, Speeches, WishStatus, SpeechStatus, SocialMedia 
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def social_media_to_dict(social_media):
    data = {
        'social_media_id': social_media.social_media_id,
        'user_id': social_media.user_id,
        'url': social_media.url,
        'created_date': social_media.created_date,
        'description': social_media.description,
        'platform': social_media.platform,
        'wish': {
            'wish_title': social_media.wish.wish_title if social_media.wish else None
        },
        'speech': {
            'speech_title': social_media.speech.speech_title if social_media.speech else None
        }
    }
    return data




def user_to_dict(user):
    return {
        'user_id': user.user_id,
        'email': user.email,
        'picture': user.picture,
        'first_name': user.first_name,
        'last_name': user.family_name
    }



def user_backend_to_dict(user):
    return {
        'user_id': user.user_id,
        'email': user.email,
        'is_mail_verified': user.is_mail_verified,
        'first_name': user.first_name,
        'phone_no': user.phone_no,
        'is_institute': user.is_institute,
        'institute_reg_number': user.institute_reg_number,
        'given_name': user.given_name,
        'address': user.address,
        'location': user.location,
        'about': user.about,
        'institute_details': user.institute_details,
        'family_name': user.family_name,
        'link': user.link,
        'picture': user.picture,
        'locale': user.locale,
        'had': None,  # This field is not in the original model, adjust as needed
        'latitude': user.latitude,
        'longitude': user.longitude,
    }


def wish_to_dict(wish):
    return {
        'wish_id': wish.wish_id,
        'wish_title': wish.wish_title,
        'wish_description': wish.wish_description,
        'created_by': user_to_dict(wish.created_by),
        'picked_by': [user_to_dict(user) for user in wish.wish_status.picked_by.all()] if hasattr(wish, 'wish_status') else [],
        'is_picked': wish.is_picked == 'true',
        'status': wish.wish_status.status if hasattr(wish, 'wish_status') else None,
        'is_verified': wish.is_verified,
        'category': wish.category,
        'location': wish.location,
        'latitude': wish.latitude,
        'longitude': wish.longitude,
        'created_date': wish.created_date.strftime('%Y-%m-%d %H:%M:%S'),
    }



def speech_to_dict(speech):
    return {
        'speech_id': speech.speech_id,
        'speech_title': speech.speech_title,
        'speech_description': speech.speech_description,
        'created_by': user_to_dict(speech.created_by),
        'picked_by': [user_to_dict(user) for user in speech.speech_status.picked_by.all()] if hasattr(speech, 'speech_status') else [],
        'is_picked': speech.is_picked == 'true',
        'status': speech.speech_status.status if hasattr(speech, 'speech_status') else None,
        'is_verified': speech.is_verified,
        'category': speech.category,
        'location': speech.location,
        'latitude': speech.latitude,
        'longitude': speech.longitude,
        'platform_url': speech.platform_url,
        'created_date': speech.created_date.strftime('%Y-%m-%d %H:%M:%S'),
    }




@csrf_exempt  # Disable CSRF protection for this view (for demo purposes)
@require_POST  # Ensure only POST requests are allowed
def create_user(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    
    # Extract data from JSON payload
    email = data.get('email')
    first_name = data.get('first_name')
    phone_no = data.get('phone_no')
    is_institute = data.get('is_institute', False)
    institute_reg_number = data.get('institute_reg_number', None)
    given_name = data.get('given_name', None)
    address = data.get('address', None)
    location = data.get('location', None)
    about = data.get('about', None)
    institute_details = data.get('institute_details', None)
    family_name = data.get('family_name', None)
    link = data.get('link', None)
    picture = data.get('picture', None)
    locale = data.get('locale', None)
    latitude = data.get('latitude', None)
    longitude = data.get('longitude', None)
    extra_field = data.get('extra_field', None)

    # Validate required fields
    if not email or not first_name:
        return JsonResponse({'success': False, 'error': 'Email and First Name are required'}, status=400)

    # Validate and create the user
    try:
        user = SeekersInstitutes.objects.create(
            email=email,
            first_name=first_name,
            phone_no=phone_no,
            is_institute=is_institute,
            institute_reg_number=institute_reg_number,
            given_name=given_name,
            address=address,
            location=location,
            about=about,
            institute_details=institute_details,
            family_name=family_name,
            link=link,
            picture=picture,
            locale=locale,
            latitude=latitude,
            longitude=longitude,
            extra_field=extra_field
        )
        return JsonResponse({'success': True, 'data': {'message': 'User created successfully', 'user_id': user.user_id}}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def create_wish(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

    
    # Extract data from JSON payload
    wish_title = data.get('wish_title')
    wish_description = data.get('wish_description')
    user_id = data.get('user_id')
    category = data.get('category')
    location = data.get('location')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Validate required fields
    if not wish_title or not wish_description or not user_id:
        return JsonResponse({'success': False, 'error': 'Wish Title, Wish Description, and User ID are required'}, status=400)


    # Create the wish and its status
    try:
        # Assuming you have a method to fetch the user object from user_id
        user = SeekersInstitutes.objects.get(pk=user_id)
        
        # Create the wish
        wish = Wishes.objects.create(
            wish_title=wish_title,
            wish_description=wish_description,
            created_by=user,
            category=category,
            location=location,
            latitude=latitude,
            longitude=longitude
        )
        
        # Create the wish status
        WishStatus.objects.create(
            wish=wish,
            status='Created'  # Default status when wish is created
        )

        return JsonResponse({'success': True, 'data': {'message': 'Wish created successfully', 'wish_id': wish.wish_id}}, status=201)
    

    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User does not exist'}, status=404)

    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@csrf_exempt
@require_POST
def create_speech(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    
    # Extract data from JSON payload
    speech_title = data.get('speech_title')
    speech_description = data.get('speech_description')
    user_id = data.get('user_id')
    category = data.get('category')
    location = data.get('location')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    platform_url = data.get('platform_url')

    # Validate required fields
    if not speech_title or not speech_description or not user_id:
        return JsonResponse({'success': False, 'error': 'Speech Title, Speech Description, and User ID are required'}, status=400)


    # Create the speech and its status
    try:
        # Assuming you have a method to fetch the user object from user_id
        user = SeekersInstitutes.objects.get(pk=user_id)
        
        # Create the speech
        speech = Speeches.objects.create(
            speech_title=speech_title,
            speech_description=speech_description,
            created_by=user,
            category=category,
            location=location,
            latitude=latitude,
            longitude=longitude,
            platform_url=platform_url
        )
        
        # Create the speech status
        SpeechStatus.objects.create(
            speech=speech,
            status='Created'  # Default status when speech is created
        )

        return JsonResponse({'success': True, 'data': {'message': 'Speech created successfully', 'speech_id': speech.speech_id}}, status=201)

    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User does not exist'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def pick_wish(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
    # Extract data from JSON payload
    wish_id = data.get('wish_id')
    user_id = data.get('user_id')

    # Validate required fields
    if not wish_id or not user_id:
        return JsonResponse({'error': 'Wish ID and User ID are required'}, status=400)

    try:
        # Fetch the wish object
        wish = Wishes.objects.get(wish_id=wish_id)

        # Check if the user has already picked this wish
        wish_status, created = WishStatus.objects.get_or_create(wish=wish)
        if SeekersInstitutes.objects.filter(pk=user_id).exists():
            user = SeekersInstitutes.objects.get(pk=user_id)
            if user in wish_status.picked_by.all():
                return JsonResponse( {'success': False, 'error': 'User has already picked this wish'}, status=400)
        else:
            return JsonResponse( {'success': False, 'error': 'Invalid User ID'}, status=400)

        # Update WishStatus and pick the wish
        wish_status.status = 'In-Progress'
        wish.is_picked = 'true'
        
        # Add the user to picked_by field
        wish_status.picked_by.add(user)
        wish_status.save()

        return JsonResponse( {'success': True, 'data': {'message': 'Wish picked successfully', 'wish_id': wish_id}}, status=200)
    
    except Wishes.DoesNotExist:
        return JsonResponse( { 'success': False, 'error': 'Wish does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse ({ 'success': False, 'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def pick_speech(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse( {'success': False, 'error': 'Invalid JSON format'}, status=400)
    
    # Extract data from JSON payload
    speech_id = data.get('speech_id')
    user_id = data.get('user_id')

    # Validate required fields
    if not speech_id or not user_id:
        return JsonResponse( {'success': False, 'error': 'Speech ID and User ID are required'}, status=400)

    try:
        # Fetch the speech object
        speech = Speeches.objects.get(speech_id=speech_id)

        # Check if the user has already picked this speech
        speech_status, created = SpeechStatus.objects.get_or_create(speech=speech)
        if SeekersInstitutes.objects.filter(pk=user_id).exists():
            user = SeekersInstitutes.objects.get(pk=user_id)
            if user in speech_status.picked_by.all():
                return JsonResponse( {'success': False, 'error': 'User has already picked this speech'}, status=400)
        else:
            return JsonResponse( {'success': False, 'error': 'Invalid User ID'}, status=400)

        # Update SpeechStatus and pick the speech
        speech_status.status = 'In-Progress'
        speech.is_picked = 'true'
        
        # Add the user to picked_by field
        speech_status.picked_by.add(user)
        speech_status.save()

        return JsonResponse( {'success': True, 'data': {'message': 'Speech picked successfully', 'speech_id': speech_id}}, status=200)
    
    except Speeches.DoesNotExist:
        return JsonResponse( {'success': False, 'error': 'Speech does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@require_GET
def list_wishes(request):
    wishes = Wishes.objects.all().select_related('wish_status', 'created_by')
    paginator = Paginator(wishes, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    wishes_list = [wish_to_dict(wish) for wish in page_obj]

    return JsonResponse({
        'success': True,
        'data': {
            'items': wishes_list,
            'total_pages': paginator.num_pages , 
            'count': paginator.count,
            'has_next' : page_obj.has_next(), 
            'has_previous' : page_obj.has_previous()
        }
    })



@require_GET
def list_speeches(request):
    speeches = Speeches.objects.all().select_related('speech_status', 'created_by')
    paginator = Paginator(speeches, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    speeches_list = [speech_to_dict(speech) for speech in page_obj]

    return JsonResponse({
        'success': True,
        'data':  {
            'items': speeches_list,
            'total_pages': paginator.num_pages , 
            'has_next' : page_obj.has_next(), 
            'count': paginator.count,
            'has_previous' : page_obj.has_previous()
        }
    })




@require_GET
def wish_by_category(request, category):
    wishes = Wishes.objects.filter(category__iexact=category).select_related('wish_status', 'created_by').order_by('created_date')
    paginator = Paginator(wishes, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    wishes_list = [wish_to_dict(wish) for wish in page_obj]

    return JsonResponse({
        'success': True,
        'data': {
            'items': wishes_list,
            'total_pages': paginator.num_pages , 
            'count': paginator.count,
            'has_next' : page_obj.has_next(), 
            'has_previous' : page_obj.has_previous()
        }
    })



@require_GET
def user_wishes(request, user_id):
    try:
        wishes = Wishes.objects.filter(created_by_id=user_id).select_related('wish_status', 'created_by').order_by('-created_date')
        paginator = Paginator(wishes, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        wishes_list = [wish_to_dict(wish) for wish in page_obj]

        return JsonResponse({
            'success': True,
            'data': {
                'items': wishes_list,
                'total_pages': paginator.num_pages , 
                'count': paginator.count,
                'has_next' : page_obj.has_next(), 
                'has_previous' : page_obj.has_previous()
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


@require_GET
def wishes_by_location_view(request):
    try:
        latitude = float(request.GET.get('latitude'))
        longitude = float(request.GET.get('longitude'))
        radius = float(request.GET.get('radius', 10))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid or missing latitude, longitude, or radius parameters'}, status=400)

    wishes = Wishes.objects.all().select_related('wish_status', 'created_by')
    nearby_wishes = []

    for wish in wishes:
        wish_lat, wish_lon = wish.latitude, wish.longitude
        if wish_lat is not None and wish_lon is not None:
            distance = haversine(latitude, longitude, wish_lat, wish_lon)
            if distance <= radius:
                nearby_wishes.append(wish)

    if not nearby_wishes:
        return JsonResponse({'success': True, 'data': {
            "items": [] , 
            'total_pages': 0, 
            'count': 0,
            'has_next': False, 
            'has_previous': False
        }}, status=200)

    page = request.GET.get('page', 1)
    paginator = Paginator(nearby_wishes, 10)

    try:
        wishes_page = paginator.page(page)
    except PageNotAnInteger:
        wishes_page = paginator.page(1)
    except EmptyPage:
        wishes_page = paginator.page(paginator.num_pages)

    data = {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'has_next': wishes_page.has_next(),
        'has_previous': wishes_page.has_previous(),
        'items': [wish_to_dict(wish) for wish in wishes_page.object_list]
    }

    return JsonResponse({'success': True, 'data': data}, safe=False)



@require_GET
def check_user_exists(request):
    try:
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'success': False, 'error': 'Email parameter is required'}, status=400)

        try:
            user = SeekersInstitutes.objects.get(email=email)
            user_data = user_backend_to_dict(user)
            return JsonResponse({'success': True, 'data': {'user_exists': True, 'user_data': user_data}}, status=200)
        except SeekersInstitutes.DoesNotExist:
            return JsonResponse({'success': True, 'data': {'user_exists': False}}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@require_GET    
def get_categories(request):
    try:
        speech_categories = Speeches.objects.values_list('category', flat=True).distinct()
        wish_categories = Wishes.objects.values_list('category', flat=True).distinct()
        
        all_categories = set(list(speech_categories) + list(wish_categories) + [
            "Education", "Personal", "Other", "Technology", "Finance", "Travel", "Environment",
            "Hobbies", "Entrepreneurship", "Spirituality and Religion", "Entertainment",
            "Literature", "Music", "Lifestyle"
        ])
        
        return JsonResponse({'success': True, 'data': {'categories': list(all_categories)}}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@require_GET
def get_wish_details(request, wishID):
    try:
        wish = get_object_or_404(Wishes, wish_id=wishID)
        wish_details = wish_to_dict(wish)
        return JsonResponse({'success': True, 'data': wish_details}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def get_speech_details(request, speechID):
    try:
        speech = get_object_or_404(Speeches, speech_id=speechID)
        speech_details = speech_to_dict(speech)
        return JsonResponse({'success': True, 'data': speech_details}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@require_GET
def get_user_speeches(request, userID):

    try:
        user = get_object_or_404(SeekersInstitutes, user_id=userID)
        speeches = Speeches.objects.filter(created_by=user).select_related('speech_status')
        
        speeches_data = [speech_to_dict(speech) for speech in speeches]
        
        return JsonResponse({'success': True, 'data': {'speeches': speeches_data}}, status=200)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@csrf_exempt
@require_POST
def create_social_media_post(request):

    try:
        data = json.loads(request.body)
        url = data.get('url')
        description = data.get('description')
        platform = data.get('platform')
        user_id = data.get('user_id')

        if not user_id:
            return JsonResponse({'success': False, 'error': 'User ID is required'}, status=400)

        # Check if the request contains either wish_id or speech_id
        if 'wish_id' in data:
            wish_id = data['wish_id']
            wish = Wishes.objects.get(pk=wish_id)
            user = SeekersInstitutes.objects.get(pk=user_id)
            social_media = SocialMedia.objects.create(wish=wish, url=url, description=description, platform=platform, user=user)
            return JsonResponse( {'success': True, 'data': {'message': f'Social media entry created for Wish {wish_id}' , 'social_media_id': social_media.social_media_id }  }, status=201)
        

        elif 'speech_id' in data:
            speech_id = data['speech_id']
            speech = Speeches.objects.get(pk=speech_id)
            user = SeekersInstitutes.objects.get(pk=user_id)
            social_media = SocialMedia.objects.create(speech=speech, url=url, description=description, platform=platform , user=user)
            return JsonResponse({'success': True, 'data': {'message': f'Social media entry created for Speech {speech_id}' ,  'social_media_id': social_media.social_media_id }  }, status=201)
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request payload'}, status=400)
    
    except KeyError:
        return JsonResponse({'success': False, 'error': 'Missing required fields in request payload'}, status=400)
    
    except Wishes.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Wish does not exist'}, status=404)
    
    except Speeches.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Speech does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    



@csrf_exempt
@require_GET
def event(request):
    is_completed = request.GET.get('isCompleted', 'false').lower() == 'true'
    page_number = request.GET.get('page', 1)
    items_per_page = 10  # You can adjust this number as needed
    
    social_media_entries = SocialMedia.objects.select_related('wish', 'speech').all()
    
    if is_completed:
        social_media_entries = social_media_entries.filter(
            Q(wish__wish_status__status='Completed') | Q(speech__speech_status__status='Completed')
        )
    
    paginator = Paginator(social_media_entries, items_per_page)
    page_obj = paginator.get_page(page_number)
    
    formatted_items = [social_media_to_dict(item) for item in page_obj.object_list]
    
    return JsonResponse({
        'success': True,
        'data': {
            'items': formatted_items,
            'total_pages': paginator.num_pages,
            'count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    }, safe=False)


def event_by_id(request, event_type, event_id):
    if event_type not in ['wish', 'speech']:
        return JsonResponse({
            'success': False,
            'error': 'Invalid event type. Must be either "wish" or "speech".'
        }, status=400)

    try:
        if event_type == 'wish':
            wish = get_object_or_404(Wishes, wish_id=event_id)
            social_media = SocialMedia.objects.filter(wish=wish).first()
        else:  # speech
            speech = get_object_or_404(Speeches, speech_id=event_id)
            social_media = SocialMedia.objects.filter(speech=speech).first()

        if not social_media:
            return JsonResponse({
                'success': False,
                'error': f'No social media entry found for the given {event_type} ID'
            }, status=404)

        data = {
            'social_media_id': social_media.social_media_id,
            'wish_id': social_media.wish.wish_id if social_media.wish else None,
            'speech_id': social_media.speech.speech_id if social_media.speech else None,
            'url': social_media.url,
            'description': social_media.description,
            'created_date': social_media.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'platform': social_media.platform,
            'wish': wish_to_dict(social_media.wish) if social_media.wish else None,
            'speech': speech_to_dict(social_media.speech) if social_media.speech else None,
        }

        return JsonResponse({
            'success': True,
            'data': data
        })

    except (Wishes.DoesNotExist, Speeches.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': f'No {event_type} found with the given ID'
        }, status=404)


@csrf_exempt
@require_GET
def event_speech(request):
    is_completed = request.GET.get('isCompleted', 'false').lower() == 'true'
    
    if is_completed:
        social_media_entries = SocialMedia.objects.filter(speech__speech_status__status='Completed').values()
    else:
        social_media_entries = SocialMedia.objects.filter(speech__isnull=False).values()
    
    return JsonResponse({'success': True, 'data': list(social_media_entries)}, safe=False)



@csrf_exempt
@require_GET
def speeches_by_category(request, category):
    try:
        page_number = request.GET.get('page', 1)
        items_per_page = 10  # You can adjust this number as needed

        speeches = Speeches.objects.filter(category=category).select_related('speech_status', 'created_by')
        
        paginator = Paginator(speeches, items_per_page)
        page_obj = paginator.get_page(page_number)
        
        speeches_list = [speech_to_dict(speech) for speech in page_obj]
        
        return JsonResponse({
            'success': True,
            'data': {
                'items': speeches_list,
                'total_pages': paginator.num_pages,
                'count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }, safe=False, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def speeches_by_location_view(request):
    try:
        latitude = float(request.GET.get('latitude'))
        longitude = float(request.GET.get('longitude'))
        radius = float(request.GET.get('radius', 20))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid or missing latitude, longitude, or radius parameters'}, status=400)

    speeches = Speeches.objects.all().select_related('speech_status', 'created_by')
    nearby_speeches = []
    for speech in speeches:
        speech_lat, speech_lon = speech.latitude, speech.longitude
        if speech_lat is not None and speech_lon is not None:
            distance = haversine(latitude, longitude, speech_lat, speech_lon)
            if distance <= radius:
                nearby_speeches.append(speech)

    if not nearby_speeches:
        return JsonResponse({'success': True, 'data': {
            "items": [] , 
            'total_pages': 0, 
            'count': 0,
            'has_next': False, 
            'has_previous': False
        }}, status=200)

    page = request.GET.get('page', 1)
    paginator = Paginator(nearby_speeches, 10)

    try:
        speeches_page = paginator.page(page)
    except PageNotAnInteger:
        speeches_page = paginator.page(1)
    except EmptyPage:
        speeches_page = paginator.page(paginator.num_pages)

    data = {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'has_next': speeches_page.has_next(),
        'has_previous': speeches_page.has_previous(),
        'items': [speech_to_dict(speech) for speech in speeches_page.object_list]
    }

    return JsonResponse({'success': True, 'data': data}, safe=False)



@csrf_exempt
@require_POST
def update_user(request, user_id):
    try:
        data = json.loads(request.body)
        print(data)
        
        user = SeekersInstitutes.objects.get(user_id=user_id)
        
        fields_to_update = ['email', 'first_name', 'phone_no', 'address', 'location', 'about', 'link', 'picture', 'locale', 'latitude', 'longitude', 
                            'is_institute' , 'institute_reg_number' , 'given_name', 'institute_details', 'family_name']
        
        for field in fields_to_update:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        return JsonResponse({'success': True, 'data': {'message': f'User {user_id} updated successfully'}}, status=200)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'User with user_id {user_id} does not exist'}, status=404)
    
    except KeyError:
        return JsonResponse({'success': False, 'error': 'Missing required fields in request payload'}, status=400)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def change_status(request):
    try:
        data = json.loads(request.body)
        social_id = data.get('social_id')
        social = SocialMedia.objects.get(pk=social_id)
        
        if 'wish_id' in data:
            wish_id = data['wish_id']
            wish = Wishes.objects.get(pk=wish_id)
            
            if social.wish_id != wish.wish_id:
                return JsonResponse({'success': False, 'error': 'Social media entry not related to this wish'}, status=400)
            
            wish_status, created = WishStatus.objects.get_or_create(wish=wish)
            wish_status.status = 'Completed'
            wish_status.save()
            
            wish.selected_fulfillment = social
            wish.save()
            
            return JsonResponse({'success': True, 'data': {'message': f'Wish {wish_id} status updated to Completed for user {social.user.user_id}'}}, status=200)
        
        elif 'speech_id' in data:
            speech_id = data['speech_id']
            speech = Speeches.objects.get(pk=speech_id)
            
            if social.speech_id != speech.speech_id:
                return JsonResponse({'success': False, 'error': 'Social media entry not related to this speech'}, status=400)
            
            speech_status, created = SpeechStatus.objects.get_or_create(speech=speech)
            speech_status.status = 'Completed'
            speech_status.save()
            
            speech.selected_fulfillment = social
            speech.save()
            
            return JsonResponse({'success': True, 'data': {'message': f'Speech {speech_id} status updated to Completed for user {social.user.user_id}'}}, status=200)
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request payload'}, status=400)
    
    except SocialMedia.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Social media entry not found'}, status=404)
    
    except Wishes.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Wish does not exist'}, status=404)
    
    except Speeches.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Speech does not exist'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def get_fulfill_details(request):
    try:
        data = json.loads(request.body)
        
        if 'wish_id' in data:
            wish_id = data['wish_id']
            socialMedia = SocialMedia.objects.filter(wish_id=wish_id)
            

            data = [{'wish_id': item.wish.wish_id,
                     'user': user_to_dict(item.user) ,
                     'url': item.url , 
                     'social_media_id': item.social_media_id,
                     'description': item.description,
                     'platform': item.platform
                     }
                    for item in socialMedia]
            
            return JsonResponse({'success': True, 'data': data}, safe=False)
        
        elif 'speech_id' in data:
            speech_id = data['speech_id']
            socialMedia = SocialMedia.objects.filter(speech_id=speech_id)

            data = [{
                     'speech_id': item.speech.speech_id,
                     'user': user_to_dict(item.user) ,
                     'url': item.url,
                     'social_media_id': item.social_media_id,
                     'description': item.description,
                     'platform': item.platform}
                    for item in socialMedia]
            
            return JsonResponse({'success': True, 'data': data}, safe=False)
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request payload'}, status=400)
    
    except KeyError:
        return JsonResponse({'success': False, 'error': 'Missing required fields in request payload'}, status=400)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def get_social_media(request, socialMediaID):
    try:

        socialMedia = get_object_or_404(SocialMedia, social_media_id=socialMediaID)

        if not socialMedia:
            return JsonResponse({'success': False, 'error': 'Social media entry not found'}, status=404)

        data = {
            'social_media_id': socialMedia.social_media_id,
            'wish_id': socialMedia.wish.wish_id if socialMedia.wish else None,
            'speech_id': socialMedia.speech.speech_id if socialMedia.speech else None,
            'url': socialMedia.url,
            'description': socialMedia.description,
            'created_date': socialMedia.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'user': user_to_dict(socialMedia.user),
            'wish': wish_to_dict(socialMedia.wish) if socialMedia.wish else None,
            'speech': speech_to_dict(socialMedia.speech) if socialMedia.speech else None,
            'platform': socialMedia.platform,
        }

        return JsonResponse({'success': True, 'data': data }, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@require_GET
def get_user_summary(request, userID):
    try:
        user = get_object_or_404(SeekersInstitutes, user_id=userID)
    except Http404:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    created_wishes = Wishes.objects.filter(created_by=user)
    created_wishes_list = [wish_to_dict(wish) for wish in created_wishes]

    created_speeches = Speeches.objects.filter(created_by=user)
    created_speeches_list = [speech_to_dict(speech) for speech in created_speeches]

    fulfilled_wishes =   Wishes.objects.filter(
        selected_fulfillment__user=userID
    )
    fulfilled_wishes_list = [wish_to_dict(wish) for wish in fulfilled_wishes]

    fulfilled_speeches = Speeches.objects.filter(
        selected_fulfillment__user=userID
    )

    fulfilled_speeches_list = [speech_to_dict(speech) for speech in fulfilled_speeches]


    user_summary = {
        'user_details' : user_backend_to_dict(user) ,
        'wishes_created': created_wishes_list,
        'speeches_created': created_speeches_list,
        'wishes_fulfilled': fulfilled_wishes_list,
        'speeches_fulfilled': fulfilled_speeches_list,
    }

    return JsonResponse({'success': True, 'data': user_summary}, safe=False)



@csrf_exempt
@require_GET
def user_details(request, userID):
    try:
        user = SeekersInstitutes.objects.get(user_id=userID)
        user_data = user_backend_to_dict(user)
        return JsonResponse({'success': True, 'data': user_data}, status=200)

    except SeekersInstitutes.DoesNotExist:

        return JsonResponse({ 'success': False, 'error': 'User does not exist'}, status=404)
    


@csrf_exempt
@require_http_methods(["POST"])
def sign_up_user_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        mandatory_fields = ['email', 'password', 'first_name', 'phone_no']
        missing_fields = [field for field in mandatory_fields if field not in data]

        if missing_fields:
            return JsonResponse({'error': f'Missing fields: {", ".join(missing_fields)}'}, status=400)

        email = data['email']
        password = data['password']
        first_name = data['first_name']
        phone_no = data['phone_no']
        is_institute = data.get('is_institute', False)

        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        user = User.objects.create_user(username=email, email=email, password=password)
        data = SeekersInstitutes.objects.create(
            email=email,
            first_name=first_name,
            phone_no=phone_no,
            is_institute=is_institute,
            is_mail_verified=False
        )

    

        response = user_to_dict(data)
        print(response)

        return JsonResponse({'message': 'User registered successfully', 'data':response, 'success':True}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def sign_in_view(request):
    try:
        # Parse JSON payload
        data = json.loads(request.body.decode('utf-8'))

        # Extract credentials
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            # Fetch SeekersInstitutes information
            seeker_institute = SeekersInstitutes.objects.get(email=user.email)

            data = user_backend_to_dict(seeker_institute)
            # print(data)
            
            # Prepare response data with user and SeekersInstitutes information
            response_data = {
                'data': data,
                'success': True
                
            }
            
            return JsonResponse(response_data, status=200)
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': 'User details not found in SeekersInstitutes'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)    

@require_http_methods(["POST"])
def sign_out_view(request):
    try:
        # Log the user out by flushing the session
        request.session.flush()
        return JsonResponse({'message': 'Successfully signed out'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)