from django.db import models
from django.contrib.auth.models import User
import uuid

class NewsSubmission(models.Model):
    SUBMISSION_TYPE_CHOICES = [
        ('article', 'Full Article'),
        ('url', 'URL'),
        ('text', 'Text Content'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    PREDICTION_CHOICES = [
        ('fake', 'Fake News'),
        ('real', 'Real News'),
        ('uncertain', 'Uncertain'),
    ]
    
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_submissions')
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES)
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(max_length=1000, blank=True, null=True)
    
    # ML Prediction Results
    prediction = models.CharField(max_length=20, choices=PREDICTION_CHOICES, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    fake_probability = models.FloatField(blank=True, null=True)
    real_probability = models.FloatField(blank=True, null=True)
    
    # Analysis Details
    flagged_keywords = models.JSONField(blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    source_credibility = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Admin moderation
    is_flagged = models.BooleanField(default=False)
    admin_reviewed = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title[:50]} - {self.prediction}"
    
    class Meta:
        db_table = 'news_submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['prediction']),
        ]

class MLModelVersion(models.Model):
    MODEL_TYPE_CHOICES = [
        ('logistic_regression', 'Logistic Regression'),
        ('random_forest', 'Random Forest'),
        ('naive_bayes', 'Naive Bayes'),
        ('bert', 'BERT Transformer'),
        ('lstm', 'LSTM Neural Network'),
    ]
    
    version_name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    model_file = models.FileField(upload_to='ml_models/')
    vectorizer_file = models.FileField(upload_to='ml_models/', blank=True, null=True)
    
    # Performance Metrics
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    
    # Metadata
    training_dataset_size = models.IntegerField()
    training_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.version_name} - {self.model_type}"
    
    class Meta:
        db_table = 'ml_model_versions'
        ordering = ['-created_at']
