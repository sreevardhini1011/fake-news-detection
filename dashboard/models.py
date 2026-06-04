from django.db import models
from django.contrib.auth.models import User

class UserNotification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('verification_complete', 'Verification Complete'),
        ('trending_fake_news', 'Trending Fake News'),
        ('system_alert', 'System Alert'),
        ('feedback_response', 'Feedback Response'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        db_table = 'user_notifications'
        ordering = ['-created_at']

class SystemAnalytics(models.Model):
    date = models.DateField(unique=True)
    total_submissions = models.IntegerField(default=0)
    fake_news_detected = models.IntegerField(default=0)
    real_news_detected = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    avg_confidence_score = models.FloatField(default=0.0)
    total_feedbacks = models.IntegerField(default=0)
    total_reports = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Analytics for {self.date}"
    
    class Meta:
        db_table = 'system_analytics'
        ordering = ['-date']
