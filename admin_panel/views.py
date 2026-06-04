from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from news_verification.models import NewsSubmission, MLModelVersion
from feedback.models import ContentReport, UserFeedback
from accounts.models import UserProfile
from dashboard.models import SystemAnalytics
import json
import os
from django.conf import settings
from django.core.files import File as DjangoFile

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with system overview"""
    
    # System statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7)).count()
    total_submissions = NewsSubmission.objects.count()
    pending_reports = ContentReport.objects.filter(status='pending').count()
    
    # Today's statistics (use timezone-aware range to avoid DB date mismatch)
    now = timezone.now()
    tz = timezone.get_current_timezone()
    today_start = now.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_submissions = NewsSubmission.objects.filter(created_at__gte=today_start, created_at__lt=today_end).count()
    today_fake = NewsSubmission.objects.filter(
        created_at__gte=today_start, created_at__lt=today_end, prediction__iexact='fake'
    ).count()
    today_real = NewsSubmission.objects.filter(
        created_at__gte=today_start, created_at__lt=today_end, prediction__iexact='real'
    ).count()
    
    # Model performance
    active_model = MLModelVersion.objects.filter(is_active=True).first()
    
    # Weekly trend
    week_data = []
    for i in range(7):
        d = now - timedelta(days=i)
        date_obj = d.date()
        count = NewsSubmission.objects.filter(created_at__date=date_obj).count()
        week_data.append({'date': date_obj.strftime('%Y-%m-%d'), 'count': count})
    
    # Recent flagged submissions
    flagged_submissions = NewsSubmission.objects.filter(is_flagged=True, admin_reviewed=False)[:5]
    
    # Pending reports
    pending_reports_list = ContentReport.objects.filter(status='pending')[:5]
    # Recent user feedbacks (latest 5)
    recent_feedbacks = UserFeedback.objects.select_related('user', 'submission').order_by('-created_at')[:5]
    total_feedbacks = UserFeedback.objects.count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_submissions': total_submissions,
        'pending_reports': pending_reports,
        'today_submissions': today_submissions,
        'today_fake': today_fake,
        'today_real': today_real,
        'active_model': active_model,
        'week_data': json.dumps(week_data),
        'flagged_submissions': flagged_submissions,
        'pending_reports_list': pending_reports_list,
        'recent_feedbacks': recent_feedbacks,
        'total_feedbacks': total_feedbacks,
    }
    
    return render(request, 'admin_panel/admin_dashboard.html', context)

@staff_member_required
def user_management(request):
    """Manage users - view, suspend, delete"""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        target_user = get_object_or_404(User, id=user_id)
        
        if action == 'suspend':
            target_user.profile.is_suspended = True
            target_user.profile.suspension_reason = request.POST.get('reason', '')
            target_user.profile.save()
            messages.success(request, f'User {target_user.username} suspended successfully')
        
        elif action == 'activate':
            target_user.profile.is_suspended = False
            target_user.profile.suspension_reason = None
            target_user.profile.save()
            messages.success(request, f'User {target_user.username} activated successfully')
        
        elif action == 'delete':
            username = target_user.username
            target_user.delete()
            messages.success(request, f'User {username} deleted successfully')
        
        elif action == 'change_role':
            new_role = request.POST.get('role')
            target_user.profile.user_type = new_role
            target_user.profile.save()
            messages.success(request, f'User role updated to {new_role}')
        
        return redirect('admin_panel:user_management')
    
    return render(request, 'admin_panel/user_management.html', {'users': users})

@staff_member_required
def content_moderation(request):
    """Review and moderate flagged content"""
    flagged_submissions = NewsSubmission.objects.filter(
        Q(is_flagged=True) | Q(reports__status='pending')
    ).distinct().order_by('-created_at')
    
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        action = request.POST.get('action')
        submission = get_object_or_404(NewsSubmission, submission_id=submission_id)
        
        if action == 'approve':
            submission.admin_reviewed = True
            submission.is_flagged = False
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.admin_notes = request.POST.get('notes', '')
            submission.save()
            messages.success(request, 'Content approved')
        
        elif action == 'reject':
            submission.admin_reviewed = True
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.admin_notes = request.POST.get('notes', '')
            submission.save()
            messages.success(request, 'Content rejected')
        
        return redirect('admin_panel:content_moderation')
    
    return render(request, 'admin_panel/content_moderation.html', {'submissions': flagged_submissions})

@staff_member_required
def model_management(request):
    """Manage ML models - view performance, upload new models"""
    models = MLModelVersion.objects.all().order_by('-created_at')

    # If no models in DB, attempt to auto-sync local repo model .pkl files
    if not models.exists():
        repo_models_dir = os.path.join(settings.BASE_DIR, 'news_verification', 'ml_models')
        if os.path.isdir(repo_models_dir):
            for fname in os.listdir(repo_models_dir):
                # look for model files (e.g., random_forest_model.pkl)
                if not fname.endswith('_model.pkl'):
                    continue

                version_name = os.path.splitext(fname)[0]
                # skip existing entries
                if MLModelVersion.objects.filter(version_name=version_name).exists():
                    continue

                # infer model type from filename
                lower = fname.lower()
                if 'logistic' in lower:
                    mtype = 'logistic_regression'
                elif 'random_forest' in lower or 'randomforest' in lower:
                    mtype = 'random_forest'
                elif 'naive_bayes' in lower or 'naivebayes' in lower:
                    mtype = 'naive_bayes'
                else:
                    mtype = 'logistic_regression'

                # create DB entry with placeholder metrics
                model_obj = MLModelVersion.objects.create(
                    version_name=version_name,
                    model_type=mtype,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    training_dataset_size=0,
                    description='Auto-created from repository model file',
                    created_by=None,
                )

                # save the file into the configured MEDIA storage
                model_path = os.path.join(repo_models_dir, fname)
                try:
                    with open(model_path, 'rb') as f:
                        model_obj.model_file.save(fname, DjangoFile(f), save=True)

                    # attach vectorizer if present
                    vect_name = fname.replace('_model.pkl', '_vectorizer.pkl')
                    vect_path = os.path.join(repo_models_dir, vect_name)
                    if os.path.exists(vect_path):
                        with open(vect_path, 'rb') as vf:
                            model_obj.vectorizer_file.save(vect_name, DjangoFile(vf), save=True)
                except Exception:
                    # if saving fails, delete the DB entry to avoid partial records
                    model_obj.delete()
                    continue

            # refresh queryset after potential inserts
            models = MLModelVersion.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'activate':
            model_id = request.POST.get('model_id')
            # Deactivate all models
            MLModelVersion.objects.update(is_active=False)
            # Activate selected model
            target_model = get_object_or_404(MLModelVersion, id=model_id)
            target_model.is_active = True
            target_model.save()
            messages.success(request, f'Model {target_model.version_name} activated')
        
        return redirect('admin_panel:model_management')
    
    return render(request, 'admin_panel/model_management.html', {'models': models})

@staff_member_required
def system_analytics(request):
    """System-wide analytics and reporting"""
    
    # Overall statistics
    total_submissions = NewsSubmission.objects.count()
    fake_count = NewsSubmission.objects.filter(prediction__iexact='fake').count()
    real_count = NewsSubmission.objects.filter(prediction__iexact='real').count()
    
    # Average confidence score
    from django.db.models import Avg
    avg_confidence = NewsSubmission.objects.aggregate(
        avg_conf=Avg('confidence_score')
    )['avg_conf'] or 0
    
    # Feedback statistics
    total_feedbacks = UserFeedback.objects.count()
    correct_predictions = UserFeedback.objects.filter(feedback_type='correct').count()
    incorrect_predictions = UserFeedback.objects.filter(feedback_type='incorrect').count()
    
    # Monthly trend - FIX: Convert date to string for JSON serialization
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_stats = NewsSubmission.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra({'date': "DATE(created_at)"}).values('date').annotate(
        total=Count('id'),
        fake=Count('id', filter=Q(prediction__iexact='fake')),
        real=Count('id', filter=Q(prediction__iexact='real'))
    ).order_by('date')
    
    # Convert date objects to strings for JSON serialization
    daily_stats_list = []
    for stat in daily_stats:
        daily_stats_list.append({
            'date': stat['date'].strftime('%Y-%m-%d') if hasattr(stat['date'], 'strftime') else str(stat['date']),
            'total': stat['total'],
            'fake': stat['fake'],
            'real': stat['real']
        })
    
    context = {
        'total_submissions': total_submissions,
        'fake_count': fake_count,
        'real_count': real_count,
        'avg_confidence': round(avg_confidence, 2),
        'total_feedbacks': total_feedbacks,
        'correct_predictions': correct_predictions,
        'incorrect_predictions': incorrect_predictions,
        'daily_stats': json.dumps(daily_stats_list),
        'accuracy_rate': round((correct_predictions / total_feedbacks * 100), 2) if total_feedbacks > 0 else 0,
    }
    
    return render(request, 'admin_panel/system_analytics.html', context)
