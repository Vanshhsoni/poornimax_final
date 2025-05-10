from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('<str:username>/', views.chat_view, name='chat_with_user'),
    path('<str:username>/poll/', views.poll_new_messages, name='poll_messages'),
]
