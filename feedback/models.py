from django.db import models
from django.contrib.auth.models import User
from news_verification.models import NewsSubmission

class UserFeedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('correct', 'Prediction Correct'),
        ('incorrect', 'Prediction Incorrect'),
        ('partially_correct', 'Partially Correct'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    submission = models.ForeignKey(NewsSubmission, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    comments = models.TextField(blank=True, null=True)
    user_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback by {self.user.username} - {self.feedback_type}"
    
    class Meta:
        db_table = 'user_feedbacks'
        unique_together = ['user', 'submission']

class ContentReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('spam', 'Spam'),
        ('misleading', 'Misleading Classification'),
        ('offensive', 'Offensive Content'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    submission = models.ForeignKey(NewsSubmission, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    admin_notes = models.TextField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Report by {self.reporter.username} - {self.report_type}"
    
    class Meta:
        db_table = 'content_reports'
        ordering = ['-created_at']
