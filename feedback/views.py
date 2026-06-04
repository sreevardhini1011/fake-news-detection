from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserFeedback, ContentReport
from news_verification.models import NewsSubmission
from .forms import FeedbackForm, ReportForm

@login_required
def submit_feedback(request, submission_id):
    """Submit feedback on news verification"""
    submission = get_object_or_404(NewsSubmission, submission_id=submission_id, user=request.user)
    
    # Check if feedback already exists
    existing_feedback = UserFeedback.objects.filter(user=request.user, submission=submission).first()
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=existing_feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.submission = submission
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('news:submission_detail', submission_id=submission_id)
    else:
        form = FeedbackForm(instance=existing_feedback)
    
    return render(request, 'feedback/submit_feedback.html', {'form': form, 'submission': submission})

@login_required
def report_content(request, submission_id):
    """Report suspicious or misclassified content"""
    submission = get_object_or_404(NewsSubmission, submission_id=submission_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.submission = submission
            report.save()
            
            # Flag the submission
            submission.is_flagged = True
            submission.save()
            
            messages.success(request, 'Report submitted successfully. Our team will review it.')
            return redirect('news:submission_detail', submission_id=submission_id)
    else:
        form = ReportForm()
    
    return render(request, 'feedback/report_content.html', {'form': form, 'submission': submission})
