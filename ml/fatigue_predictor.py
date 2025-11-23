"""
XGBoost-based fatigue prediction for nurses.
Predicts physical and emotional fatigue to improve scheduling and well-being.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import pickle


class FatiguePredictor:
    """
    Predicts nurse fatigue levels based on:
    - Work history (hours, consecutive days)
    - Shift patterns (night shifts, weekends)
    - Personal factors (age, experience, preferences)
    - Schedule quality (preference matching)
    """
    
    def __init__(self):
        self.physical_model = None
        self.emotional_model = None
        self.feature_names = []
        self.is_trained = False
        self.label_encoders = {}
    
    def extract_features(self, nurse_history: Dict) -> Dict:
        """
        Extract features for fatigue prediction.
        
        Args:
            nurse_history: Dictionary containing:
                - nurse_id: str
                - shifts_last_week: List[Dict] (shift info)
                - shifts_last_month: List[Dict]
                - personal_info: Dict (age, experience, etc.)
                - preferences: Dict
        
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Work intensity features
        last_week_shifts = nurse_history.get('shifts_last_week', [])
        last_month_shifts = nurse_history.get('shifts_last_month', [])
        
        # Hours worked
        features['hours_last_week'] = sum(
            s.get('duration', 0) for s in last_week_shifts
        )
        features['hours_last_month'] = sum(
            s.get('duration', 0) for s in last_month_shifts
        )
        
        # Consecutive working days
        if last_week_shifts:
            dates = sorted([s['date'] for s in last_week_shifts])
            consecutive = 1
            max_consecutive = 1
            for i in range(1, len(dates)):
                if (dates[i] - dates[i-1]).days == 1:
                    consecutive += 1
                    max_consecutive = max(max_consecutive, consecutive)
                else:
                    consecutive = 1
            features['max_consecutive_days'] = max_consecutive
        else:
            features['max_consecutive_days'] = 0
        
        # Shift pattern features
        night_shifts_week = sum(
            1 for s in last_week_shifts 
            if s.get('shift_type') == 'night'
        )
        features['night_shifts_last_week'] = night_shifts_week
        
        weekend_shifts_month = sum(
            1 for s in last_month_shifts
            if s['date'].weekday() in [4, 5]  # Friday, Saturday
        )
        features['weekend_shifts_last_month'] = weekend_shifts_month
        
        # Days since last rest
        if last_week_shifts:
            last_shift_date = max(s['date'] for s in last_week_shifts)
            features['days_since_last_rest'] = (datetime.now() - last_shift_date).days
        else:
            features['days_since_last_rest'] = 7
        
        # Personal factors
        personal = nurse_history.get('personal_info', {})
        features['age'] = personal.get('age', 30)
        features['years_experience'] = personal.get('experience', 5)
        features['has_children'] = 1 if personal.get('has_children', False) else 0
        
        # Preference matching
        prefs = nurse_history.get('preferences', {})
        features['preference_match_rate'] = self._calculate_preference_match(
            last_week_shifts, prefs
        )
        
        # Workload vs capacity
        max_hours = personal.get('max_hours_per_week', 48)
        features['workload_ratio'] = features['hours_last_week'] / max_hours
        
        # Shift variety (entropy of shift types)
        shift_types = [s.get('shift_type', 'unknown') for s in last_week_shifts]
        features['shift_variety'] = self._calculate_entropy(shift_types)
        
        return features
    
    def _calculate_preference_match(self, shifts: List[Dict], 
                                    preferences: Dict) -> float:
        """Calculate how well shifts match nurse preferences"""
        if not shifts:
            return 1.0
        
        preferred_shifts = set(preferences.get('preferred_shifts', []))
        avoided_shifts = set(preferences.get('avoided_shifts', []))
        
        matches = 0
        for shift in shifts:
            shift_type = shift.get('shift_type')
            if shift_type in preferred_shifts:
                matches += 1
            elif shift_type in avoided_shifts:
                matches -= 1
        
        return max(0, min(1, (matches + len(shifts)) / (2 * len(shifts))))
    
    def _calculate_entropy(self, items: List) -> float:
        """Calculate Shannon entropy of a list"""
        if not items:
            return 0.0
        
        from collections import Counter
        counts = Counter(items)
        total = len(items)
        
        entropy = 0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return entropy
    
    def prepare_training_data(self, 
                             historical_records: List[Dict]) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """
        Prepare training data from historical records.
        
        Args:
            historical_records: List of dictionaries containing:
                - nurse_history: Dict (as in extract_features)
                - physical_fatigue: float (0-1)
                - emotional_fatigue: float (0-1)
        
        Returns:
            X: Feature DataFrame
            y_physical: Physical fatigue scores
            y_emotional: Emotional fatigue scores
        """
        features_list = []
        physical_fatigue = []
        emotional_fatigue = []
        
        for record in historical_records:
            features = self.extract_features(record['nurse_history'])
            features_list.append(features)
            physical_fatigue.append(record.get('physical_fatigue', 0))
            emotional_fatigue.append(record.get('emotional_fatigue', 0))
        
        X = pd.DataFrame(features_list)
        self.feature_names = X.columns.tolist()
        
        return X, np.array(physical_fatigue), np.array(emotional_fatigue)
    
    def train(self, historical_records: List[Dict], 
              test_size: float = 0.2, random_state: int = 42):
        """
        Train XGBoost models for physical and emotional fatigue.
        
        Args:
            historical_records: Training data
            test_size: Fraction of data for testing
            random_state: Random seed
        """
        print("Preparing training data...")
        X, y_physical, y_emotional = self.prepare_training_data(historical_records)
        
        # Split data
        X_train, X_test, y_phys_train, y_phys_test, y_emot_train, y_emot_test = \
            train_test_split(X, y_physical, y_emotional, 
                           test_size=test_size, random_state=random_state)
        
        # XGBoost parameters
        params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': random_state,
            'eval_metric': 'rmse'
        }
        
        # Train physical fatigue model
        print("\nTraining physical fatigue model...")
        self.physical_model = xgb.XGBRegressor(**params)
        self.physical_model.fit(
            X_train, y_phys_train,
            eval_set=[(X_test, y_phys_test)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Evaluate physical model
        y_phys_pred = self.physical_model.predict(X_test)
        phys_rmse = np.sqrt(mean_squared_error(y_phys_test, y_phys_pred))
        phys_r2 = r2_score(y_phys_test, y_phys_pred)
        print(f"Physical Fatigue - RMSE: {phys_rmse:.4f}, R²: {phys_r2:.4f}")
        
        # Train emotional fatigue model
        print("\nTraining emotional fatigue model...")
        self.emotional_model = xgb.XGBRegressor(**params)
        self.emotional_model.fit(
            X_train, y_emot_train,
            eval_set=[(X_test, y_emot_test)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Evaluate emotional model
        y_emot_pred = self.emotional_model.predict(X_test)
        emot_rmse = np.sqrt(mean_squared_error(y_emot_test, y_emot_pred))
        emot_r2 = r2_score(y_emot_test, y_emot_pred)
        print(f"Emotional Fatigue - RMSE: {emot_rmse:.4f}, R²: {emot_r2:.4f}")
        
        self.is_trained = True
        print("\nTraining completed successfully!")
        
        return {
            'physical': {'rmse': phys_rmse, 'r2': phys_r2},
            'emotional': {'rmse': emot_rmse, 'r2': emot_r2}
        }
    
    def predict(self, nurse_history: Dict) -> Dict[str, float]:
        """
        Predict fatigue levels for a nurse.
        
        Args:
            nurse_history: Nurse work history and personal info
        
        Returns:
            Dictionary with physical_fatigue and emotional_fatigue scores (0-1)
        """
        if not self.is_trained:
            # Return default values if not trained
            return {
                'physical_fatigue': 0.5,
                'emotional_fatigue': 0.5,
                'overall_fatigue': 0.5
            }
        
        # Extract features
        features = self.extract_features(nurse_history)
        X = pd.DataFrame([features])[self.feature_names]
        
        # Predict
        physical = float(self.physical_model.predict(X)[0])
        emotional = float(self.emotional_model.predict(X)[0])
        
        # Clip to [0, 1]
        physical = max(0, min(1, physical))
        emotional = max(0, min(1, emotional))
        
        # Overall fatigue (weighted average)
        overall = 0.6 * physical + 0.4 * emotional
        
        return {
            'physical_fatigue': physical,
            'emotional_fatigue': emotional,
            'overall_fatigue': overall
        }
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Get feature importance for both models"""
        if not self.is_trained:
            return {}
        
        physical_importance = dict(zip(
            self.feature_names,
            self.physical_model.feature_importances_
        ))
        
        emotional_importance = dict(zip(
            self.feature_names,
            self.emotional_model.feature_importances_
        ))
        
        return {
            'physical': physical_importance,
            'emotional': emotional_importance
        }
    
    def save(self, path: str):
        """Save models"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        checkpoint = {
            'physical_model': self.physical_model,
            'emotional_model': self.emotional_model,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        with open(path, 'wb') as f:
            pickle.dump(checkpoint, f)
        
        print(f"Models saved to {path}")
    
    def load(self, path: str):
        """Load models"""
        with open(path, 'rb') as f:
            checkpoint = pickle.load(f)
        
        self.physical_model = checkpoint['physical_model']
        self.emotional_model = checkpoint['emotional_model']
        self.feature_names = checkpoint['feature_names']
        self.is_trained = checkpoint['is_trained']
        
        print(f"Models loaded from {path}")


def generate_sample_fatigue_data(num_samples: int = 1000) -> List[Dict]:
    """Generate synthetic fatigue data for testing"""
    records = []
    
    for _ in range(num_samples):
        # Generate random work history
        hours_last_week = np.random.uniform(20, 60)
        consecutive_days = np.random.randint(0, 8)
        night_shifts = np.random.randint(0, 5)
        
        # Physical fatigue correlates with hours and consecutive days
        physical = (
            0.3 * (hours_last_week / 60) +
            0.3 * (consecutive_days / 7) +
            0.2 * (night_shifts / 4) +
            0.2 * np.random.random()
        )
        physical = max(0, min(1, physical))
        
        # Emotional fatigue correlates with preference matching and variety
        preference_match = np.random.random()
        workload_ratio = hours_last_week / 48
        
        emotional = (
            0.4 * (1 - preference_match) +
            0.3 * workload_ratio +
            0.3 * np.random.random()
        )
        emotional = max(0, min(1, emotional))
        
        record = {
            'nurse_history': {
                'shifts_last_week': [
                    {
                        'date': datetime.now() - timedelta(days=i),
                        'duration': np.random.uniform(6, 12),
                        'shift_type': np.random.choice(['morning', 'afternoon', 'night'])
                    }
                    for i in range(int(hours_last_week / 8))
                ],
                'shifts_last_month': [],
                'personal_info': {
                    'age': np.random.randint(25, 55),
                    'experience': np.random.randint(1, 20),
                    'has_children': np.random.choice([True, False]),
                    'max_hours_per_week': 48
                },
                'preferences': {
                    'preferred_shifts': ['morning'],
                    'avoided_shifts': ['night']
                }
            },
            'physical_fatigue': physical,
            'emotional_fatigue': emotional
        }
        
        records.append(record)
    
    return records


if __name__ == "__main__":
    print("Generating sample fatigue data...")
    data = generate_sample_fatigue_data(num_samples=1000)
    
    print("Initializing fatigue predictor...")
    predictor = FatiguePredictor()
    
    print("Training models...")
    results = predictor.train(data, test_size=0.2)
    
    print("\nFeature importance:")
    importance = predictor.get_feature_importance()
    for model_type, features in importance.items():
        print(f"\n{model_type.capitalize()} fatigue:")
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
        for feat, imp in sorted_features[:5]:
            print(f"  {feat}: {imp:.4f}")
    
    print("\nSaving models...")
    predictor.save("fatigue_predictor.pkl")
    
    print("\nTesting prediction...")
    test_nurse = {
        'shifts_last_week': [
            {
                'date': datetime.now() - timedelta(days=i),
                'duration': 8,
                'shift_type': 'night' if i % 3 == 0 else 'morning'
            }
            for i in range(6)
        ],
        'shifts_last_month': [],
        'personal_info': {'age': 35, 'experience': 8, 'has_children': True, 'max_hours_per_week': 48},
        'preferences': {'preferred_shifts': ['morning'], 'avoided_shifts': ['night']}
    }
    
    prediction = predictor.predict(test_nurse)
    print(f"\nPredicted fatigue levels:")
    print(f"  Physical: {prediction['physical_fatigue']:.2f}")
    print(f"  Emotional: {prediction['emotional_fatigue']:.2f}")
    print(f"  Overall: {prediction['overall_fatigue']:.2f}")
