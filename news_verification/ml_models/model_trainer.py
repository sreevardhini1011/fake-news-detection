import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import os

class FakeNewsModelTrainer:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.vectorizer = None
        self.model = None
        
    def load_and_preprocess_data(self):
        """Load and preprocess the dataset"""
        print("Loading dataset...")
        df = pd.read_csv(self.dataset_path)
        
        # Combine title and text
        df['combined_text'] = df['title'] + " " + df['text']
        
        # Handle missing values
        df['combined_text'] = df['combined_text'].fillna('')
        
        # Basic text cleaning
        df['combined_text'] = df['combined_text'].str.lower()
        df['combined_text'] = df['combined_text'].str.replace(r'[^\w\s]', ' ', regex=True)
        
        X = df['combined_text']
        y = df['label']
        
        return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    def train_logistic_regression(self, X_train, y_train, X_test, y_test):
        """Train Logistic Regression model"""
        print("\nTraining Logistic Regression Model...")
        
        # Vectorize text
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train model
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.model.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        self.print_metrics(y_test, y_pred)
        
        # Save models
        self.save_models('logistic_regression')
        
        return self.model, self.vectorizer
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train Random Forest model"""
        print("\nTraining Random Forest Model...")
        
        self.vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_vec, y_train)
        
        y_pred = self.model.predict(X_test_vec)
        self.print_metrics(y_test, y_pred)
        
        self.save_models('random_forest')
        
        return self.model, self.vectorizer
    
    def train_naive_bayes(self, X_train, y_train, X_test, y_test):
        """Train Naive Bayes model"""
        print("\nTraining Naive Bayes Model...")
        
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        self.model = MultinomialNB()
        self.model.fit(X_train_vec, y_train)
        
        y_pred = self.model.predict(X_test_vec)
        self.print_metrics(y_test, y_pred)
        
        self.save_models('naive_bayes')
        
        return self.model, self.vectorizer
    
    def print_metrics(self, y_test, y_pred):
        """Print evaluation metrics"""
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}")
        print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Fake', 'Real']))
    
    def save_models(self, model_name):
        """Save trained model and vectorizer"""
        model_dir = 'news_verification/ml_models'
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = f'{model_dir}/{model_name}_model.pkl'
        vectorizer_path = f'{model_dir}/{model_name}_vectorizer.pkl'
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)
        
        print(f"\nModel saved to: {model_path}")
        print(f"Vectorizer saved to: {vectorizer_path}")

def main():
    # Initialize trainer
    trainer = FakeNewsModelTrainer('datasets/fake_news_data.csv')
    
    # Load and split data
    X_train, X_test, y_train, y_test = trainer.load_and_preprocess_data()
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train different models
    print("\n" + "="*50)
    trainer.train_logistic_regression(X_train, y_train, X_test, y_test)
    
    print("\n" + "="*50)
    trainer.train_random_forest(X_train, y_train, X_test, y_test)
    
    print("\n" + "="*50)
    trainer.train_naive_bayes(X_train, y_train, X_test, y_test)

if __name__ == "__main__":
    main()
