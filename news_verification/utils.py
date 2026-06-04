import joblib
import os
import re
import numpy as np
from django.conf import settings

class NewsVerifier:
    def __init__(self, model_type='logistic_regression'):
        self.model_type = model_type
        model_dir = os.path.join(settings.BASE_DIR, 'news_verification', 'ml_models')
        
        model_path = os.path.join(model_dir, f'{model_type}_model.pkl')
        vectorizer_path = os.path.join(model_dir, f'{model_type}_vectorizer.pkl')
        
        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords(self, text, top_n=10):
        """Extract important keywords from text"""
        # Simple keyword extraction based on TF-IDF scores
        text_vec = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top features
        dense = text_vec.todense()
        dense_list = dense.tolist()[0]
        phrase_scores = [pair for pair in zip(range(0, len(dense_list)), dense_list) if pair[1] > 0]
        
        sorted_phrases = sorted(phrase_scores, key=lambda t: t[1], reverse=True)
        keywords = [feature_names[word_id] for word_id, score in sorted_phrases[:top_n]]
        
        return keywords
    
    def predict(self, title, content):
        """Make prediction on news article"""
        # Combine and preprocess
        combined_text = f"{title} {content}"
        cleaned_text = self.preprocess_text(combined_text)
        
        # Vectorize
        text_vec = self.vectorizer.transform([cleaned_text])
        
        # Predict
        prediction = self.model.predict(text_vec)[0]
        probabilities = self.model.predict_proba(text_vec)[0]
        
        # Extract keywords
        keywords = self.extract_keywords(cleaned_text)
        
        # Calculate sentiment (simple heuristic)
        sentiment = self.calculate_sentiment(combined_text)
        
        # Determine prediction label
        pred_label = 'real' if prediction == 1 else 'fake'
        confidence = max(probabilities) * 100
        
        result = {
            'prediction': pred_label,
            'confidence_score': round(confidence, 2),
            'fake_probability': round(probabilities[0] * 100, 2),
            'real_probability': round(probabilities[1] * 100, 2),
            'flagged_keywords': keywords,
            'sentiment_score': round(sentiment, 2),
            'explanation': self.generate_explanation(pred_label, confidence, keywords)
        }
        
        return result
    
    def calculate_sentiment(self, text):
        """Simple sentiment calculation"""
        # Placeholder - in production, use proper sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'positive', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'negative', 'horrible', 'worst']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total
    
    def generate_explanation(self, prediction, confidence, keywords):
        """Generate human-readable explanation"""
        if prediction == 'fake':
            explanation = f"This content has been classified as likely FAKE with {confidence:.1f}% confidence. "
            explanation += f"Key indicators include suspicious patterns and language commonly associated with misinformation. "
            explanation += f"Flagged keywords: {', '.join(keywords[:5])}"
        else:
            explanation = f"This content appears to be REAL with {confidence:.1f}% confidence. "
            explanation += f"The language and structure are consistent with credible news reporting. "
            explanation += f"Key terms: {', '.join(keywords[:5])}"
        
        return explanation
