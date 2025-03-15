from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Poll, Option, Participant, TextResponse
import uuid
from wordcloud import WordCloud
import io
import base64
from django.urls import reverse

# Helper function to generate a word cloud image
def generate_word_cloud(responses):
    text = " ".join(response.response for response in responses)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')


@login_required
def create_poll(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        question_type = request.POST.get('question_type')
        expiration_time = request.POST.get('expiration_time') or None

        # Create the poll
        poll = Poll.objects.create(
            creator=request.user,
            question=question,
            question_type=question_type,
            expiration_time=expiration_time
        )

        # Add options for multiple-choice polls
        if question_type == 'MC':
            options = request.POST.getlist('options')
            for option_text in options:
                Option.objects.create(poll=poll, text=option_text)

        # Generate the poll link
        poll_link = request.build_absolute_uri(reverse('polls:poll_detail', args=[poll.uuid]))

        return render(request, 'create_poll.html', {'poll_link': poll_link, 'user_polls': Poll.objects.filter(creator=request.user)})

    return render(request, 'create_poll.html', {'user_polls': Poll.objects.filter(creator=request.user)})


@login_required
def user_polls(request):
    user_polls = Poll.objects.filter(creator=request.user)
    return render(request, 'user_polls.html', {'user_polls': user_polls})


from django.core.exceptions import PermissionDenied

def poll_detail(request, poll_uuid):
    poll = get_object_or_404(Poll, uuid=poll_uuid)
    participant_id = request.COOKIES.get('participant_id')

    # Check if the poll is active and not expired
    if not poll.can_accept_responses():
        return render(request, 'poll_closed.html', {'poll': poll})

    # Check if the participant has already responded
    if participant_id:
        try:
            participant = Participant.objects.get(identifier=participant_id, poll=poll)
            if participant.has_responded:
                return render(request, 'poll_already_responded.html', {'poll': poll})
        except Participant.DoesNotExist:
            pass

    # Handle response submission
    if request.method == 'POST':
        if not participant_id:
            # Create a new participant
            participant = Participant.objects.create(poll=poll)
            response = HttpResponse(status=204)
            response.set_cookie('participant_id', participant.identifier)
        else:
            participant = Participant.objects.get(identifier=participant_id, poll=poll)

        if poll.question_type == 'MC':
            # Handle multiple-choice response
            option_id = request.POST.get('option')
            option = Option.objects.get(id=option_id)
            option.votes += 1
            option.save()
        else:
            # Handle open-text response
            response_text = request.POST.get('response')
            TextResponse.objects.create(poll=poll, participant=participant, response=response_text)

        participant.has_responded = True
        participant.save()
        return redirect('polls:poll_results', poll_uuid=poll.uuid)

    # Only the creator can see the activate/deactivate toggle and other management options
    is_creator = request.user == poll.creator

    return render(request, 'poll_detail.html', {
        'poll': poll,
        'is_creator': is_creator,
    })




def poll_results(request, poll_uuid):
    poll = get_object_or_404(Poll, uuid=poll_uuid)

    if poll.question_type == 'MC':
        # Get vote counts for multiple-choice polls
        options = poll.options.all()
        results = [{'text': option.text, 'votes': option.votes} for option in options]
        word_cloud = None
    else:
        # Get visible responses for open-text polls
        visible_responses = TextResponse.objects.filter(poll=poll, is_active=True).exclude(
            expiration_time__lt=timezone.now()
        )
        results = [{'response': response.response} for response in visible_responses]
        word_cloud = generate_word_cloud(visible_responses)

    return render(request, 'poll_results.html', {
        'poll': poll,
        'results': results,
        'word_cloud': word_cloud
    })

@login_required
def toggle_poll_active(request, poll_uuid):
    poll = get_object_or_404(Poll, uuid=poll_uuid, creator=request.user)
    poll.is_active = not poll.is_active
    poll.save()
    return JsonResponse({'is_active': poll.is_active})

@login_required
def toggle_response_active(request, response_id):
    response = get_object_or_404(TextResponse, id=response_id, poll__creator=request.user)
    response.is_active = not response.is_active
    response.save()
    return JsonResponse({'is_active': response.is_active})

@login_required
def set_response_expiration(request, response_id):
    response = get_object_or_404(TextResponse, id=response_id, poll__creator=request.user)
    expiration_time = request.POST.get('expiration_time')
    response.expiration_time = expiration_time
    response.save()
    return JsonResponse({'expiration_time': response.expiration_time})


def poll_closed(request):
    return render(request, 'poll_closed.html')

def poll_already_responded(request):
    return render(request, 'poll_already_responded.html')