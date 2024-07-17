# social_connect_app/views.py

from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from math import radians, sin, cos, sqrt, atan2
from django.shortcuts import get_object_or_404 
from django.db.models import Q
from .models import SeekersInstitutes, Wishes, Speeches, WishStatus, SpeechStatus, SocialMedia, CompletionDetails
import json


@csrf_exempt  # Disable CSRF protection for this view (for demo purposes)
@require_POST  # Ensure only POST requests are allowed
def create_user(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
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
        return JsonResponse({'error': 'Email and First Name are required'}, status=400)

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
        return JsonResponse({'message': 'User created successfully', 'user_id': user.user_id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def create_wish(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
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
        return JsonResponse({'error': 'Wish Title, Wish Description, and User ID are required'}, status=400)

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

        return JsonResponse({'message': 'Wish created successfully', 'wish_id': wish.wish_id}, status=201)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)    


@csrf_exempt
@require_POST
def create_speech(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
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
        return JsonResponse({'error': 'Speech Title, Speech Description, and User ID are required'}, status=400)

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

        return JsonResponse({'message': 'Speech created successfully', 'speech_id': speech.speech_id}, status=201)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
                return JsonResponse({'error': 'User has already picked this wish'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid User ID'}, status=400)

        # Update WishStatus and pick the wish
        wish_status.status = 'In-Progress'
        wish.is_picked = 'true'
        
        # Add the user to picked_by field
        wish_status.picked_by.add(user)
        wish_status.save()

        return JsonResponse({'message': 'Wish picked successfully', 'wish_id': wish_id}, status=200)
    
    except Wishes.DoesNotExist:
        return JsonResponse({'error': 'Wish does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def pick_speech(request):
    # Parse request body as JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
    # Extract data from JSON payload
    speech_id = data.get('speech_id')
    user_id = data.get('user_id')

    # Validate required fields
    if not speech_id or not user_id:
        return JsonResponse({'error': 'Speech ID and User ID are required'}, status=400)

    try:
        # Fetch the speech object
        speech = Speeches.objects.get(speech_id=speech_id)

        # Check if the user has already picked this speech
        speech_status, created = SpeechStatus.objects.get_or_create(speech=speech)
        if SeekersInstitutes.objects.filter(pk=user_id).exists():
            user = SeekersInstitutes.objects.get(pk=user_id)
            if user in speech_status.picked_by.all():
                return JsonResponse({'error': 'User has already picked this speech'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid User ID'}, status=400)

        # Update SpeechStatus and pick the speech
        speech_status.status = 'In-Progress'
        speech.is_picked = 'true'
        
        # Add the user to picked_by field
        speech_status.picked_by.add(user)
        speech_status.save()

        return JsonResponse({'message': 'Speech picked successfully', 'speech_id': speech_id}, status=200)
    
    except Speeches.DoesNotExist:
        return JsonResponse({'error': 'Speech does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@require_GET
def list_wishes(request):
    wishes = Wishes.objects.all().select_related('wish_status')
    paginator = Paginator(wishes, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    wishes_list = []
    for wish in page_obj:
        picked_by_users = [{
            'name': user.first_name,
            'user_id': user.user_id,  # Adjust to match your actual user ID field name
            'status': wish.wish_status.status
        } for user in wish.wish_status.picked_by.all()]
        
        wishes_list.append({
            'wish_id': wish.wish_id,
            'wish_title': wish.wish_title,
            'wish_description': wish.wish_description,
            'created_by_id': wish.created_by.user_id, 
            'created_by': wish.created_by.first_name,
            'picked_by': picked_by_users,
            'status': wish.wish_status.status,
            'category': wish.category,
            'location': wish.location,
            'latitude': wish.latitude,
            'longitude': wish.longitude,
            'created_date': wish.created_date.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return JsonResponse({'wishes': wishes_list, 'total_pages': paginator.num_pages})


@require_GET
def list_speeches(request):
    speeches = Speeches.objects.all().select_related('speech_status')
    paginator = Paginator(speeches, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    speeches_list = []
    for speech in page_obj:
        picked_by_users = [{
            'name': user.first_name,
            'user_id': user.user_id,  # Adjust to match your actual user ID field name
            'status': speech.speech_status.status  # Assuming status is the same for all picked_by users
        } for user in speech.speech_status.picked_by.all()]
        
        speeches_list.append({
            'speech_id': speech.speech_id,
            'speech_title': speech.speech_title,
            'speech_description': speech.speech_description,
            'created_by_id': speech.created_by.user_id, 
            'created_by': speech.created_by.first_name,
            'picked_by': picked_by_users,
            'status': speech.speech_status.status,
            'category': speech.category,
            'location': speech.location,
            'latitude': speech.latitude,
            'longitude': speech.longitude,
            'created_date': speech.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'platform_url': speech.platform_url,
        })

    return JsonResponse({'speeches': speeches_list, 'total_pages': paginator.num_pages})



def wish_by_category(request, category):
    # Fetch wishes for the given category and order them by some field
    wishes = Wishes.objects.filter(category=category).select_related('wish_status').order_by('created_date')

    # Pagination
    paginator = Paginator(wishes, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Prepare response data
    wishes_list = []
    for wish in page_obj:
        picked_by_users = [{
            'name': user.first_name,
            'user_id': user.user_id,  # Adjust to match your actual user ID field name
            'status': wish.wish_status.status  # Assuming status is the same for all picked_by users
        } for user in wish.wish_status.picked_by.all()]

        wishes_list.append({
            'wish_id': wish.wish_id,
            'wish_title': wish.wish_title,
            'wish_description': wish.wish_description,
            'created_by_id': wish.created_by.user_id, 
            'created_by': wish.created_by.first_name,
            'picked_by': picked_by_users,
            'status': wish.wish_status.status,
            'category': wish.category,
            'location': wish.location,
            'latitude': wish.latitude,
            'longitude': wish.longitude,
            'created_date': wish.created_date.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return JsonResponse({'wishes': wishes_list, 'total_pages': paginator.num_pages})


@require_GET
def user_wishes(request, user_id):
    try:
        wishes = Wishes.objects.filter(created_by_id=user_id).order_by('-created_date')
        paginator = Paginator(wishes, 10)  # 10 items per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        wishes_list = []
        for wish in page_obj:
            wishes_list.append({
                'wish_id': wish.wish_id,
                'wish_title': wish.wish_title,
                'wish_description': wish.wish_description,
                'created_by': wish.created_by.first_name,
                'status': wish.wish_status.status,
                'category': wish.category,
                'location': wish.location,
                'latitude': wish.latitude,
                'longitude': wish.longitude,
                'created_date': wish.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return JsonResponse({'wishes': wishes_list, 'total_pages': paginator.num_pages})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


# Haversine formula to calculate distance
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
        radius = float(request.GET.get('radius', 10))  # Default radius is 10 km
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid or missing latitude, longitude, or radius parameters'}, status=400)

    wishes = Wishes.objects.all()
    nearby_wishes = []

    for wish in wishes:
        wish_lat, wish_lon = wish.latitude, wish.longitude
        if wish_lat is not None and wish_lon is not None:
            distance = haversine(latitude, longitude, wish_lat, wish_lon)
            if distance <= radius:
                nearby_wishes.append(wish)

    if not nearby_wishes:
        return JsonResponse({'message': 'No wish found for given location'}, status=200)

    # Pagination
    page = request.GET.get('page')
    paginator = Paginator(nearby_wishes, 10)  # 10 wishes per page

    try:
        wishes_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        wishes_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        wishes_page = paginator.page(paginator.num_pages)

    # Prepare data to return
    data = {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': wishes_page.number,
        'has_next': wishes_page.has_next(),
        'has_previous': wishes_page.has_previous(),
        'results': [
            {
                'wish_id': wish.wish_id,
                'wish_title': wish.wish_title,
                'wish_description': wish.wish_description,
                'created_by': wish.created_by.user_id,
                'picked_by': [{
                    'user_id': user.user_id,
                    'name': user.first_name
                } for user in wish.wish_status.picked_by.all()] if wish.wish_status else None,
                'is_picked': wish.is_picked,
                'status': wish.wish_status.status if wish.wish_status else None,
                'is_verified': wish.is_verified,
                'category': wish.category,
                'location': wish.location,
                'latitude': wish.latitude,
                'longitude': wish.longitude,
                'created_date': wish.created_date,
            } for wish in wishes_page.object_list
        ]
    }

    return JsonResponse(data, safe=False)



@require_GET
def check_user_exists(request):
    email = request.GET.get('email')
    
    if not email:
        return JsonResponse({'error': 'Email parameter is required'}, status=400)
    
    user_exists = SeekersInstitutes.objects.filter(email=email).exists()
    
    return JsonResponse({'exists': user_exists})






@require_GET    
def get_categories(request):
    try:
        # Get all unique categories from Speeches and Wishes
        speech_categories = Speeches.objects.values_list('category', flat=True).distinct()
        wish_categories = Wishes.objects.values_list('category', flat=True).distinct()
        
        # Combine and deduplicate categories
        all_categories = set(list(speech_categories) + list(wish_categories))
        
        return JsonResponse({'categories': list(all_categories)}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@require_GET
def get_wish_details(request, wishID):
    try:
        # Get the wish object based on wishID
        wish = get_object_or_404(Wishes, wish_id=wishID)
        
        # Fetch wish status and related picked_by details
        try:
            wish_status = WishStatus.objects.get(wish=wish)
            picked_by = wish_status.picked_by.all()
        except WishStatus.DoesNotExist:
            picked_by = []

        # Prepare the response data
        wish_details = {
            'wish_id': wish.wish_id,
            'wish_title': wish.wish_title,
            'wish_description': wish.wish_description,
            'created_by': {
                'user_id': wish.created_by.user_id,
                'email': wish.created_by.email,
                'first_name': wish.created_by.first_name,
                'last_name': wish.created_by.family_name,
            },
            'is_picked': wish.is_picked,
            'is_verified': wish.is_verified,
            'category': wish.category,
            'location': wish.location,
            'latitude': wish.latitude,
            'longitude': wish.longitude,
            'created_date': wish.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'picked_by': [
                {
                    'user_id': picker.user_id,
                    'name': picker.first_name,
                    'status': wish_status.status if picker in picked_by else 'Not picked by this user'
                }
                for picker in picked_by
            ]
        }
        
        return JsonResponse(wish_details, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


def get_speech_details(request, speechID):
    try:
        # Get the speech object based on speechID
        speech = get_object_or_404(Speeches, speech_id=speechID)
        
        # Get speech status details
        speech_status = SpeechStatus.objects.filter(speech=speech)
        
        # Prepare picked_by details
        picked_by_list = []
        for status in speech_status:
            for picked_by in status.picked_by.all():
                picked_by_details = {
                    'user_id': picked_by.user_id,
                    'status': status.status,
                }
                picked_by_list.append(picked_by_details)
        
        # Prepare the response data
        speech_details = {
            'speech_id': speech.speech_id,
            'speech_title': speech.speech_title,
            'speech_description': speech.speech_description,
            'created_by': {
                'user_id': speech.created_by.user_id,
                'email': speech.created_by.email,
                # Add any other relevant fields from SeekersInstitutes model
            },
            'is_picked': speech.is_picked,
            'is_verified': speech.is_verified,
            'category': speech.category,
            'location': speech.location,
            'latitude': speech.latitude,
            'longitude': speech.longitude,
            'created_date': speech.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'platform_url': speech.platform_url,
            'picked_by': picked_by_list,
            # Add any other fields specific to Speeches model
        }
        
        return JsonResponse(speech_details, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_user_speeches(request, userID):
    try:
        user = get_object_or_404(SeekersInstitutes, user_id=userID)
        speeches = Speeches.objects.filter(created_by=user)
        
        # Prepare serialized data to return
        speeches_data = []
        for speech in speeches:
            speech_data = {
                'speech_id': speech.speech_id,
                'speech_title': speech.speech_title,
                'speech_description': speech.speech_description,
                'created_by': speech.created_by.first_name,  # Assuming you want to return creator's first name
                'category': speech.category,
                'location': speech.location,
                'latitude': speech.latitude,
                'longitude': speech.longitude,
                'created_date': speech.created_date.strftime('%Y-%m-%d %H:%M:%S'),  # Example date formatting
                'status': speech.speech_status.status  # Assuming you have a related model SpeechStatus
            }
            speeches_data.append(speech_data)
        
        return JsonResponse({'speeches': speeches_data}, status=200)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def create_social_media_post(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        description = data.get('description')
        platform = data.get('platform')

        # Check if the request contains either wish_id or speech_id
        if 'wish_id' in data:
            wish_id = data['wish_id']
            wish = Wishes.objects.get(pk=wish_id)
            social_media = SocialMedia.objects.create(wish=wish, url=url, description=description, platform=platform)
            return JsonResponse({'message': f'Social media entry created for Wish {wish_id}'}, status=201)
        
        elif 'speech_id' in data:
            speech_id = data['speech_id']
            speech = Speeches.objects.get(pk=speech_id)
            social_media = SocialMedia.objects.create(speech=speech, url=url, description=description, platform=platform)
            return JsonResponse({'message': f'Social media entry created for Speech {speech_id}'}, status=201)
        
        else:
            return JsonResponse({'error': 'Invalid request payload'}, status=400)
    
    except KeyError:
        return JsonResponse({'error': 'Missing required fields in request payload'}, status=400)
    
    except Wishes.DoesNotExist:
        return JsonResponse({'error': 'Wish does not exist'}, status=404)
    
    except Speeches.DoesNotExist:
        return JsonResponse({'error': 'Speech does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_GET
def event(request):
    is_completed = request.GET.get('isCompleted', 'false').lower() == 'true'
    
    if is_completed:
        # Return entries from SocialMedia where wishstatus or speech status is 'Completed'
        social_media_entries = SocialMedia.objects.filter(
            Q(wish__wish_status__status='Completed') | Q(speech__speech_status__status='Completed')
        ).values()
    else:
        # Return all entries from SocialMedia
        social_media_entries = SocialMedia.objects.all().values()
    
    return JsonResponse(list(social_media_entries), safe=False)


@csrf_exempt
@require_GET
def event_wish(request):
    is_completed = request.GET.get('isCompleted', 'false').lower() == 'true'
    
    if is_completed:
        # Return entries from SocialMedia where wishstatus status is 'Completed'
        social_media_entries = SocialMedia.objects.filter(wish__wish_status__status='Completed').values()
    else:
        # Return all wish entries from SocialMedia
        social_media_entries = SocialMedia.objects.filter(wish__isnull=False).values()
    
    return JsonResponse(list(social_media_entries), safe=False)


@csrf_exempt
@require_GET
def event_speech(request):
    is_completed = request.GET.get('isCompleted', 'false').lower() == 'true'
    
    if is_completed:
        # Return entries from SocialMedia where speech status is 'Completed'
        social_media_entries = SocialMedia.objects.filter(speech__speech_status__status='Completed').values()
    else:
        # Return all speech entries from SocialMedia
        social_media_entries = SocialMedia.objects.filter(speech__isnull=False).values()
    
    return JsonResponse(list(social_media_entries), safe=False)


@csrf_exempt
@require_GET
def user_details(request, userID):
    try:
        user = SeekersInstitutes.objects.get(user_id=userID)
        user_details = {
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
            'created_date': user.created_date,
            'latitude': user.latitude,
            'longitude': user.longitude,
            'extra_field': user.extra_field,
        }
        return JsonResponse(user_details, status=200)
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    

@csrf_exempt
@require_GET
def speeches_by_category(request, category):
    try:
        speeches = Speeches.objects.filter(category=category)
        speeches_list = []
        
        for speech in speeches:
            speech_data = {
                'speech_id': speech.speech_id,
                'speech_title': speech.speech_title,
                'speech_description': speech.speech_description,
                'created_by': speech.created_by.email,  # Example: Fetching email, adjust as per your model
                'is_picked': speech.is_picked,
                'is_verified': speech.is_verified,
                'category': speech.category,
                'location': speech.location,
                'latitude': speech.latitude,
                'longitude': speech.longitude,
                'created_date': speech.created_date,
                'platform_url': speech.platform_url,
            }
            speeches_list.append(speech_data)
        
        return JsonResponse(speeches_list, safe=False, status=200)
    
    except Speeches.DoesNotExist:
        return JsonResponse({'error': 'No speeches found for the given category'}, status=404)
    

    

@require_GET
def speeches_by_location_view(request):
    try:
        latitude = float(request.GET.get('latitude'))
        longitude = float(request.GET.get('longitude'))
        radius = float(request.GET.get('radius', 20))  # Default radius is 20 km
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid or missing latitude, longitude, or radius parameters'}, status=400)

    speeches = Speeches.objects.all()
    nearby_speeches = []

    for speech in speeches:
        speech_lat, speech_lon = speech.latitude, speech.longitude
        if speech_lat is not None and speech_lon is not None:
            distance = haversine(latitude, longitude, speech_lat, speech_lon)
            if distance <= radius:
                nearby_speeches.append(speech)

    if not nearby_speeches:
        return JsonResponse({'message': 'No speeches found for given location'}, status=200)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(nearby_speeches, 10)  # 10 speeches per page

    try:
        speeches_page = paginator.page(page)
    except PageNotAnInteger:
        speeches_page = paginator.page(1)
    except EmptyPage:
        speeches_page = paginator.page(paginator.num_pages)

    # Prepare data to return
    data = {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': speeches_page.number,
        'has_next': speeches_page.has_next(),
        'has_previous': speeches_page.has_previous(),
        'results': [
            {
                'speech_id': speech.speech_id,
                'speech_title': speech.speech_title,
                'speech_description': speech.speech_description,
                'created_by': speech.created_by.email,  # Example: Adjust based on your model structure
                'picked_by': [{
                    'user_id': user.user_id,
                    'name': user.first_name
                } for user in speech.speech_status.picked_by.all()] if speech.speech_status else None,
                'is_picked': speech.is_picked,
                'status': speech.speech_status.status if speech.speech_status else None,
                'is_verified': speech.is_verified,
                'category': speech.category,
                'location': speech.location,
                'latitude': speech.latitude,
                'longitude': speech.longitude,
                'created_date': speech.created_date,
                'platform_url': speech.platform_url,
            } for speech in speeches_page.object_list
        ]
    }

    return JsonResponse(data, safe=False)


@csrf_exempt
@require_POST
def update_user(request, user_id):
    try:
        data = json.loads(request.body)
        
        # Fetch the user object
        user = SeekersInstitutes.objects.get(user_id=user_id)
        
        # Update user fields based on JSON payload
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'phone_no' in data:
            user.phone_no = data['phone_no']
        if 'address' in data:
            user.address = data['address']
        if 'location' in data:
            user.location = data['location']
        if 'about' in data:
            user.about = data['about']
        if 'link' in data:
            user.link = data['link']
        if 'picture' in data:
            user.picture = data['picture']
        if 'locale' in data:
            user.locale = data['locale']
        if 'latitude' in data:
            user.latitude = data['latitude']
        if 'longitude' in data:
            user.longitude = data['longitude']
        
        # Save the updated user object
        user.save()
        
        return JsonResponse({'message': f'User {user_id} updated successfully'}, status=200)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': f'User with user_id {user_id} does not exist'}, status=404)
    
    except KeyError:
        return JsonResponse({'error': 'Missing required fields in request payload'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def change_status(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        picked_by_id = data.get('picked_by_id')
        
        if 'wish_id' in data:
            wish_id = data['wish_id']
            wish = Wishes.objects.get(pk=wish_id)
            
            # Update status for the specific picked_by user
            wish_status, created = WishStatus.objects.get_or_create(wish=wish)
            wish_status.picked_by.add(picked_by_id)  # Add picked_by_id to existing ManyToManyField
            
            wish_status.status = 'Completed'
            wish_status.save()

            # Create entry in CompletionDetails
            CompletionDetails.objects.create(wish=wish, completed_by_user_id=picked_by_id)
            
            return JsonResponse({'message': f'Wish {wish_id} status updated to Completed for user {picked_by_id}'}, status=200)
        
        elif 'speech_id' in data:
            speech_id = data['speech_id']
            speech = Speeches.objects.get(pk=speech_id)
            
            # Update status for the specific picked_by user
            speech_status, created = SpeechStatus.objects.get_or_create(speech=speech)
            speech_status.picked_by.add(picked_by_id)  # Add picked_by_id to existing ManyToManyField
            
            speech_status.status = 'Completed'
            speech_status.save()

            # Create entry in CompletionDetails
            CompletionDetails.objects.create(speech=speech, completed_by_user_id=picked_by_id)
            
            return JsonResponse({'message': f'Speech {speech_id} status updated to Completed for user {picked_by_id}'}, status=200)
        
        else:
            return JsonResponse({'error': 'Invalid request payload'}, status=400)
    
    except KeyError:
        return JsonResponse({'error': 'Missing required fields in request payload'}, status=400)
    
    except Wishes.DoesNotExist:
        return JsonResponse({'error': 'Wish does not exist or user does not have permission'}, status=404)
    
    except Speeches.DoesNotExist:
        return JsonResponse({'error': 'Speech does not exist or user does not have permission'}, status=404)
    
    except SeekersInstitutes.DoesNotExist:
        return JsonResponse({'error': 'Picked_by user does not exist'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def get_fulfill_details(request):
    try:
        data = json.loads(request.body)
        
        if 'wish_id' in data:
            wish_id = data['wish_id']
            details = CompletionDetails.objects.filter(wish_id=wish_id)
            data = [{'wish_id': detail.wish_id,
                     'speech_id': detail.speech_id,
                     'completed_by_user_id': detail.completed_by_user_id}
                    for detail in details]
            
            return JsonResponse(data, safe=False)
        
        elif 'speech_id' in data:
            speech_id = data['speech_id']
            details = CompletionDetails.objects.filter(speech_id=speech_id)
            data = [{'wish_id': detail.wish_id,
                     'speech_id': detail.speech_id,
                     'completed_by_user_id': detail.completed_by_user_id}
                    for detail in details]
            
            return JsonResponse(data, safe=False)
        
        else:
            return JsonResponse({'error': 'Invalid request payload'}, status=400)
    
    except KeyError:
        return JsonResponse({'error': 'Missing required fields in request payload'}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)