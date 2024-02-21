from django.urls import path
from .views import login_view, home_view, setup_view, video_view, register_data, get_visualization_data,get_user_data,get_user_count, visualizations  # Import your views
from . import admin

urlpatterns = [
    path('', login_view, name='login'),  # Path to your login view
    path('home/', home_view, name='home'),
    path('setup/', setup_view, name='setup'),
    path('video/<int:video_index>/', video_view, name='video'),  # URL for individual videos
    path('video_results/<int:video_index>/', visualizations, name='visualizations'),  # URL for individual videos
    path('register_data/', register_data, name='register_data'),
    path('get-visualization-data/', get_visualization_data, name='get_visualization_data'),
    path('get_user_data/', get_user_data, name='get_user_data'),
    path('get_user_count/', get_user_count, name='get_user_count'),
]