from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from news_verification.models import NewsSubmission
from feedback.models import UserFeedback, ContentReport
from .models import UserNotification, SystemAnalytics
import json

@login_required
def user_dashboard(request):
    """Main user dashboard with overview statistics"""
    user = request.user
    
    # Get user statistics
    total_submissions = NewsSubmission.objects.filter(user=user).count()
    fake_detected = NewsSubmission.objects.filter(user=user, prediction='fake').count()
    real_detected = NewsSubmission.objects.filter(user=user, prediction='real').count()
    pending_verifications = NewsSubmission.objects.filter(user=user, status='pending').count()
    
    # Recent submissions
    recent_submissions = NewsSubmission.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Unread notifications
    unread_notifications = UserNotification.objects.filter(user=user, is_read=False).count()
    
    # Weekly trend data for chart
    week_ago = timezone.now() - timedelta(days=7)
    weekly_qs = NewsSubmission.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).extra({'date': "DATE(created_at)"}).values('date').annotate(count=Count('id')).order_by('date')

    # Normalize dates to strings for JSON serialization
    weekly_submissions = []
    for item in weekly_qs:
        date_val = item.get('date')
        weekly_submissions.append({
            'date': date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val),
            'count': item.get('count', 0)
        })

    context = {
        'total_submissions': total_submissions,
        'fake_detected': fake_detected,
        'real_detected': real_detected,
        'pending_verifications': pending_verifications,
        'recent_submissions': recent_submissions,
        'unread_notifications': unread_notifications,
        'weekly_submissions': json.dumps(weekly_submissions),
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)

@login_required
def analytics(request):
    """Detailed analytics and trends"""
    user = request.user
    
    # Monthly statistics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    submissions = NewsSubmission.objects.filter(user=user, created_at__gte=thirty_days_ago)
    
    # Prediction breakdown
    prediction_stats = submissions.values('prediction').annotate(count=Count('id'))
    
    # Average confidence score
    from django.db.models import Avg
    avg_confidence = submissions.aggregate(avg_conf=Avg('confidence_score'))['avg_conf'] or 0
    
    # Top flagged keywords
    all_keywords = []
    for submission in submissions:
        if submission.flagged_keywords:
            all_keywords.extend(submission.flagged_keywords)
    
    from collections import Counter
    keyword_frequency = Counter(all_keywords).most_common(10)
    
    context = {
        'submissions': submissions,
        'prediction_stats': prediction_stats,
        'avg_confidence': avg_confidence,
        'keyword_frequency': keyword_frequency,
    }
    
    return render(request, 'dashboard/analytics.html', context)

@login_required
def notifications(request):
    """User notifications page"""
    notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark as read when viewing
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """Mark individual notification as read"""
    notification = UserNotification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('dashboard:notifications')
