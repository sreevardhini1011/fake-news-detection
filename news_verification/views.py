from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NewsSubmission
from .forms import NewsSubmissionForm
from .utils import NewsVerifier
from dashboard.models import UserNotification

@login_required
def submit_news(request):
    if request.method == 'POST':
        form = NewsSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.status = 'pending'
            submission.save()
            
            messages.success(request, 'News submitted for verification!')
            return redirect('news:verify_news')
    else:
        form = NewsSubmissionForm()
    
    return render(request, 'news_verification/submit_news.html', {'form': form})

@login_required
def verify_news(request):
    # Get pending submission
    submission = NewsSubmission.objects.filter(user=request.user, status='pending').first()
    
    if not submission:
        messages.info(request, 'No pending news to verify')
        return redirect('news:submit_news')
    
    try:
        # Update status
        submission.status = 'processing'
        submission.save()
        
        # Verify using ML model
        verifier = NewsVerifier(model_type='logistic_regression')
        result = verifier.predict(submission.title, submission.content)
        
        # Update submission with results
        submission.prediction = result['prediction']
        submission.confidence_score = result['confidence_score']
        submission.fake_probability = result['fake_probability']
        submission.real_probability = result['real_probability']
        submission.flagged_keywords = result['flagged_keywords']
        submission.sentiment_score = result['sentiment_score']
        submission.explanation = result['explanation']
        submission.status = 'completed'
        submission.save()
        
        # Create notification
        UserNotification.objects.create(
            user=request.user,
            notification_type='verification_complete',
            title='Verification Complete',
            message=f'Your submitted news has been verified: {result["prediction"].upper()}',
            link=f'/news/result/{submission.submission_id}/'
        )
        
        messages.success(request, 'Verification completed!')
        return redirect('news:verification_result', submission_id=submission.submission_id)
        
    except Exception as e:
        submission.status = 'failed'
        submission.error_message = str(e)
        submission.save()
        messages.error(request, f'Verification failed: {str(e)}')
        return redirect('news:submit_news')

@login_required
def verification_result(request, submission_id):
    submission = get_object_or_404(NewsSubmission, submission_id=submission_id, user=request.user)
    return render(request, 'news_verification/verification_result.html', {'submission': submission})

@login_required
def news_history(request):
    submissions = NewsSubmission.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'news_verification/news_history.html', {'submissions': submissions})

@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(NewsSubmission, submission_id=submission_id, user=request.user)
    return render(request, 'news_verification/submission_detail.html', {'submission': submission})
