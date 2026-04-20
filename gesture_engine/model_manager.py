import os
import sys
import joblib
import numpy as np

# Ensure root directory is in path for utils/config imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from utils.logger import logger

class ModelManager:
    def __init__(self, model_path, dataset_path, confidence_threshold=0.75):
        self.model_path = model_path
        self.dataset_path = dataset_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.labels = []
        
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['pipeline']
                self.labels = data['labels']
                logger.info(f"Model loaded successfully with labels: {self.labels}")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
        else:
            logger.warning("Model file not found. Training required.")

    def load_dataset(self):
        """
        Iterates through each gesture folder in the dataset path,
        loads .npy files, and builds X, y arrays.
        """
        X = []
        y = []
        
        if not os.path.exists(self.dataset_path):
            logger.error(f"Dataset path does not exist: {self.dataset_path}")
            return None, None, None

        # Labels are folder names in sorted order
        labels = sorted([d for d in os.listdir(self.dataset_path) 
                        if os.path.isdir(os.path.join(self.dataset_path, d))])
        
        if not labels:
            logger.error(f"No gesture folders found in {self.dataset_path}")
            return None, None, None
            
        for idx, label in enumerate(labels):
            label_path = os.path.join(self.dataset_path, label)
            files = [f for f in os.listdir(label_path) if f.endswith('.npy')]
            
            logger.info(f"Loading {len(files)} samples for gesture: {label}")
            for f in files:
                file_path = os.path.join(label_path, f)
                try:
                    feature_vector = np.load(file_path)
                    X.append(feature_vector)
                    y.append(idx)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
                    
        if not X:
            return None, None, None
            
        return np.array(X), np.array(y), labels

    def train(self, X, y, labels):
        """Train the model using the provided data."""
        logger.info("Training new model...")
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", SVC(probability=True, kernel='rbf'))
        ])
        
        pipeline.fit(X, y)
        self.model = pipeline
        self.labels = labels
        
        # Save model
        joblib.dump({'pipeline': pipeline, 'labels': labels}, self.model_path)
        logger.info(f"Model trained and saved to {self.model_path}")

    def predict(self, features):
        if self.model is None:
            return None, 0.0
            
        features = features.reshape(1, -1)
        probs = self.model.predict_proba(features)[0]
        max_idx = np.argmax(probs)
        confidence = probs[max_idx]
        
        if confidence >= self.confidence_threshold:
            return self.labels[max_idx], confidence
        return None, confidence
