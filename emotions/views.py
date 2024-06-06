import json
import random
from email.utils import formataddr
from statistics import multimode

from django.conf import settings
from django.contrib import messages  # For displaying messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import send_mail
from django.db.models import Avg, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import UserVideoForm
from .models import Register, Visualization
from .models import User  # Import your User model


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        action = request.POST.get('action')

        if action == 'login':
            otp = request.POST.get('otp')
            try:
                user = User.objects.get(email=email, otp=otp)
                request.session['user_id'] = user.id  # Manually set the user in the session
                messages.success(request, "Login successful!")
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, "Invalid email or OTP!")
        elif action == 'request_otp':
            try:
                user = User.objects.get(email=email)
                # Generate new OTP
                new_otp = str(random.randint(100000, 999999))
                user.otp = new_otp
                user.save()
                # Send email with new OTP
                send_email(email, new_otp)
                messages.success(request, "The new OTP has been sent to your email.")
            except User.DoesNotExist:
                messages.error(request, "Email not found! Only invited users are allowed to this app.")

    return render(request, 'login.html')


def send_email(to_email, otp):
    subject = 'New OTP'
    message = f'Your new OTP for Neuro Cinematics beta experiment (https://reaimagineapps.pythonanywhere.com/) is: {otp}'
    from_name = 'spectra'
    email_from = formataddr((from_name, settings.EMAIL_HOST_USER))
    recipient_list = [to_email]
    send_mail(subject, message, email_from, recipient_list)


def home_view(request):
    user = get_user(request)
    if user is None:
        return redirect('login')

    Visualization.objects.filter(confirmed=False, user_id=user.id).delete()

    # Check if demographic fields are filled
    if not user.age_group or not user.gender or not user.movies_per_month or not user.zip:
        return redirect('setup')  # Redirect to setup form

    visualizations = Visualization.objects.filter(
        user_id=user.id
    )
    nvisualizations = []
    for i in range(len(settings.VIDEOS)):
        nvisualizations.append(len(visualizations.filter(video_id=i)))

    videos_data = [
        {**video, 'visualizations': visualization}
        for video, visualization in zip(settings.VIDEOS, nvisualizations)
    ]
    # Render the real home page
    return render(request, 'home.html', {'videos_data': videos_data})


def setup_view(request):
    user = get_user(request)
    if user is None:
        return redirect('login')

    if request.method == 'POST':
        # Update user demographics
        age_group = request.POST.get('age_group')
        gender = request.POST.get('gender')
        movies_per_month = request.POST.get('movies_per_month')
        zip = request.POST.get('zip_code')

        # Check if all fields are filled
        if age_group and gender and movies_per_month and zip:
            user.age_group = age_group
            user.gender = gender
            user.movies_per_month = movies_per_month
            user.zip = zip
            user.save()
            return redirect('home')  # Redirect to the real home page
        else:
            # If any field is uncompleted, show an error message
            messages.error(request, "Please complete all fields.")

    # If GET request or no data submitted, render the page with the form
    return render(request, 'setup.html', {
        'user': user,
        'AGE_GROUP_CHOICES': User.AGE_GROUP_CHOICES,
        'GENDER_CHOICES': User.GENDER_CHOICES,
        'MOVIES_PER_MONTH_CHOICES': User.MOVIES_PER_MONTH_CHOICES
    })


def video_view(request, video_index):
    user = get_user(request)
    if user is None:
        return redirect('login')

    try:
        video = settings.VIDEOS[int(video_index)]  # Fetch the video by index
    except (IndexError, ValueError):
        messages.error(request, "The requested video does not exist.")  # Send an error message
        return redirect('home')  # Redirect back to the home page

    new_visualization = Visualization.objects.create(
        user=user,
        video_id=video_index,
        confirmed=False
    )
    print("New visualization created! ", new_visualization.id)

    return render(request, 'video.html', {'video': video, "visualization_id": new_visualization.id})


@csrf_exempt  # Only for demonstration; consider CSRF implications
def register_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            visualization_id = data.get('visualizationId')
            register_list = data.get('registers', [])

            # You can now use visualization_id and register_list as needed
            Register.objects.bulk_create([
                Register(
                    visualization_id=visualization_id,  # Assuming all registers belong to this visualization
                    playback_timestamp=item.get('playback_timestamp'),
                    dominantEmotion=item.get('dominant_emotion'),
                    attention=item.get('attention'),
                    emotionIntensity=item.get('emotionIntensity')
                )
                for item in register_list[:-1]])

            visualization = Visualization.objects.get(id=visualization_id)
            visualization.confirmed = True
            visualization.would_buy = register_list[-1].get("would_buy") == "true"
            visualization.amount_to_buy = register_list[-1].get("amount_to_buy") if visualization.would_buy else 0
            visualization.save()

            messages.success(request, "Your visualization was processed successfully!")
            return JsonResponse({'redirect_url': reverse('home'), 'status': 'success'})
        except Exception as e:
            print(str(e))
            messages.error(request, "There was an error processing your visualization")  # Send an error message
            return JsonResponse({'redirect_url': reverse('home'), 'status': 'error', 'message': str(e)})

    return JsonResponse({'redirect_url': reverse('home'), 'status': 'invalid_method'})


def get_visualization_data(request):
    user_id = request.GET.get('user_id')
    age = request.GET.get('age')
    gender = request.GET.get('gender')
    movies = request.GET.get('movies')
    video_id = request.GET.get('video_id')

    users = User.objects.all()
    if user_id:
        users = users.filter(id=user_id)
    if age:
        users = users.filter(age_group=age)
    if gender:
        users = users.filter(gender=gender)
    if movies:
        users = users.filter(movies_per_month=movies)

    visualizations = Visualization.objects.filter(
        confirmed=True,
        user__in=users,
        video_id=video_id
    )
    total_visualizations = visualizations.count()
    would_buy_count = visualizations.filter(would_buy=True).count()
    would_buy_percentage = (would_buy_count / total_visualizations * 100) if total_visualizations > 0 else 0
    # Calculating the mean of amount_to_buy
    average_amount_to_buy = visualizations.aggregate(Avg('amount_to_buy'))['amount_to_buy__avg'] or 0
    max_amount_to_buy = visualizations.aggregate(Max('amount_to_buy'))['amount_to_buy__max'] or 0
    amount_to_buy_values = visualizations.values_list('amount_to_buy', flat=True)
    mode_amount_to_buy = multimode(amount_to_buy_values)

    data = {
        'visualizations': [],
        'would_buy_percentage': would_buy_percentage,
        'average_amount_to_buy': average_amount_to_buy,
        'max_amount_to_buy': max_amount_to_buy,
        'mode_amount_to_buy': mode_amount_to_buy,
        "videoSrc": staticfiles_storage.url(settings.VIDEOS[int(video_id)]["path"])
    }
    for vis in visualizations:
        vis_data = list(Register.objects.filter(
            visualization=vis
        ).values('playback_timestamp', 'emotionIntensity', 'dominantEmotion'))

        data['visualizations'].append(vis_data)

    return JsonResponse(data, safe=False)


def get_user_data(request):
    user_id = request.GET.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            data = {
                'age_group': user.age_group,
                'gender': user.gender,
                'movies_per_month': user.movies_per_month,
            }
            return JsonResponse(data)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return JsonResponse({'error': 'No user ID provided'}, status=400)


def get_user_count(request):
    user_id = request.GET.get('email')
    age = request.GET.get('age_group')
    gender = request.GET.get('gender')
    movies = request.GET.get('movies_per_month')
    video_id = request.GET.get('video')  # Make sure this is correctly obtained

    users = User.objects.all()
    if user_id:
        users = users.filter(id=user_id)
    if age:
        users = users.filter(age_group=age)
    if gender:
        users = users.filter(gender=gender)
    if movies:
        users = users.filter(movies_per_month=movies)

    visCount = Visualization.objects.filter(
        confirmed=True,
        user__in=users,
        video_id=video_id
    ).count()

    return JsonResponse({'count': users.count(), "visCount": visCount})


def visualization_plot_view(request):
    if request.method == "POST":
        form = UserVideoForm(request.POST)
        if form.is_valid():
            # Process the form data and generate plot data
            # For now, just redirecting to home
            return redirect('admin:index')
    else:
        form = UserVideoForm()
    return render(request, 'admin/visualization_plot.html', {'form': form})


def visualizations(request, video_index):
    user = get_user(request)
    if user is None:
        return redirect('login')

    try:
        video = settings.VIDEOS[int(video_index)]  # Fetch the video by index
    except (IndexError, ValueError):
        messages.error(request, "The requested video does not exist.")  # Send an error message
        return redirect('home')  # Redirect back to the home page

    visualizations = Visualization.objects.filter(
        confirmed=True,
        user_id=user.id,
        video_id=video_index
    )
    if len(visualizations) == 0:
        return redirect('home')

    vis_data = list(Register.objects.filter(
        visualization=visualizations[0]
    ).values('playback_timestamp', 'emotionIntensity', 'dominantEmotion'))

    return render(request, 'visualizations.html', {'video': video, 'vis_data': json.dumps(vis_data)})


def get_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return User.objects.get(id=user_id)
