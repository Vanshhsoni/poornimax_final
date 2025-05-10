from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Message
from django.contrib.auth.decorators import login_required

User = get_user_model()

from django.http import JsonResponse

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            msg = Message.objects.create(sender=request.user, receiver=other_user, content=content)
            return JsonResponse({
                'sender': request.user.username,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'sender_is_user': True
            })

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    )
    return render(request, 'chat/chat.html', {
        'messages': messages,
        'other_user': other_user
    })


@login_required
def poll_new_messages(request, username):
    other_user = get_object_or_404(User, username=username)

    # Get last message timestamp from query param
    last_timestamp = request.GET.get('after')
    if last_timestamp:
        from django.utils.dateparse import parse_datetime
        last_dt = parse_datetime(last_timestamp)
    else:
        last_dt = timezone.now()

    new_messages = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        timestamp__gt=last_dt
    )

    data = [{
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'sender_is_user': False
    } for msg in new_messages]

    return JsonResponse(data, safe=False)

def inbox_view(request):
    user = request.user

    # Get users the current user has sent or received messages with
    sent_to = Message.objects.filter(sender=user).values_list('receiver', flat=True)
    received_from = Message.objects.filter(receiver=user).values_list('sender', flat=True)

    # Combine and remove duplicates
    user_ids = set(list(sent_to) + list(received_from))
    users = User.objects.filter(id__in=user_ids)

    return render(request, 'chat/inbox.html', {'users': users})