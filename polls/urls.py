from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    # Poll creation and management
    path('create/', views.create_poll, name='create_poll'),
    path('user-polls/', views.user_polls, name='user_polls'),

    # Poll participation
    path('poll/<uuid:poll_uuid>/', views.poll_detail, name='poll_detail'),
    path('poll/<uuid:poll_uuid>/results/', views.poll_results, name='poll_results'),

    # Poll activation and response management
    path('poll/<uuid:poll_uuid>/toggle/', views.toggle_poll_active, name='toggle_poll_active'),
    path('response/<int:response_id>/toggle/', views.toggle_response_active, name='toggle_response_active'),
    path('response/<int:response_id>/expire/', views.set_response_expiration, name='set_response_expiration'),

    # Error pages
    path('poll-closed/', views.poll_closed, name='poll_closed'),
    path('already-responded/', views.poll_already_responded, name='poll_already_responded'),
]