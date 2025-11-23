"""
LSTM-based demand forecasting for patient flow and nurse requirements.
Specifically designed for Egyptian healthcare patterns.
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import pickle


class DemandLSTM(nn.Module):
    """
    LSTM model for forecasting nurse demand based on:
    - Historical patient flow
    - Day of week patterns
    - Seasonal trends
    - Special events (Ramadan, holidays)
    """
    
    def __init__(self, input_size: int = 10, hidden_size: int = 64, 
                 num_layers: int = 2, output_size: int = 3):
        super(DemandLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, output_size)
        )
    
    def forward(self, x):
        """
        Forward pass
        x shape: (batch_size, sequence_length, input_size)
        """
        # LSTM forward
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layers
        output = self.fc(last_output)
        
        return output


class DemandForecaster:
    """
    Demand forecasting system for nurse scheduling.
    Predicts required nurses per shift type for future dates.
    """
    
    def __init__(self, sequence_length: int = 14, device: str = "cpu"):
        """
        Args:
            sequence_length: Number of historical days to use for prediction
            device: 'cpu' or 'cuda'
        """
        self.sequence_length = sequence_length
        self.device = torch.device(device)
        
        # Model
        self.model = DemandLSTM(
            input_size=10,  # Features per day
            hidden_size=64,
            num_layers=2,
            output_size=3  # Morning, Afternoon, Night shift demands
        ).to(self.device)
        
        # Scalers
        self.feature_scaler = MinMaxScaler()
        self.target_scaler = MinMaxScaler()
        
        self.is_trained = False
    
    def prepare_features(self, date: datetime, 
                        historical_data: Optional[pd.DataFrame] = None) -> np.ndarray:
        """
        Prepare feature vector for a given date.
        
        Features:
        1. Day of week (one-hot: 7 features)
        2. Is weekend
        3. Is Ramadan
        4. Is public holiday
        5. Patient count (if historical data available)
        6. Week of year (normalized)
        7. Month (normalized)
        """
        features = []
        
        # Day of week (one-hot)
        day_of_week = date.weekday()
        day_one_hot = [1 if i == day_of_week else 0 for i in range(7)]
        features.extend(day_one_hot)
        
        # Is weekend (Friday in Egypt)
        is_weekend = 1 if day_of_week == 4 else 0  # Friday
        features.append(is_weekend)
        
        # Week of year (normalized)
        week_of_year = date.isocalendar()[1] / 52.0
        features.append(week_of_year)
        
        # Month (normalized)
        month_normalized = date.month / 12.0
        features.append(month_normalized)
        
        # If we have 10 features, pad or trim
        while len(features) < 10:
            features.append(0)
        
        return np.array(features[:10])
    
    def create_sequences(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for training.
        
        Args:
            data: DataFrame with columns ['date', 'morning_demand', 'afternoon_demand', 'night_demand']
        
        Returns:
            X: sequences of features (N, sequence_length, input_size)
            y: target demands (N, 3)
        """
        X, y = [], []
        
        # Sort by date
        data = data.sort_values('date').reset_index(drop=True)
        
        for i in range(len(data) - self.sequence_length):
            # Get sequence of features
            sequence_dates = data.iloc[i:i + self.sequence_length]['date']
            sequence_features = [
                self.prepare_features(date) 
                for date in sequence_dates
            ]
            
            # Get target (next day's demand)
            target_row = data.iloc[i + self.sequence_length]
            target = [
                target_row['morning_demand'],
                target_row['afternoon_demand'],
                target_row['night_demand']
            ]
            
            X.append(sequence_features)
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def train(self, historical_data: pd.DataFrame, 
              epochs: int = 100, batch_size: int = 32, 
              learning_rate: float = 0.001, validation_split: float = 0.2):
        """
        Train the demand forecasting model.
        
        Args:
            historical_data: DataFrame with columns 
                            ['date', 'morning_demand', 'afternoon_demand', 'night_demand']
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            validation_split: Fraction of data for validation
        """
        # Create sequences
        X, y = self.create_sequences(historical_data)
        
        # Scale targets
        y = self.target_scaler.fit_transform(y)
        
        # Split train/validation
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Convert to tensors
        X_train = torch.FloatTensor(X_train).to(self.device)
        y_train = torch.FloatTensor(y_train).to(self.device)
        X_val = torch.FloatTensor(X_val).to(self.device)
        y_val = torch.FloatTensor(y_val).to(self.device)
        
        # Training setup
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=10
        )
        
        # Training loop
        best_val_loss = float('inf')
        train_losses, val_losses = [], []
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i + batch_size]
                batch_y = y_train[i:i + batch_size]
                
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= (len(X_train) / batch_size)
            train_losses.append(train_loss)
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = criterion(val_outputs, y_val).item()
                val_losses.append(val_loss)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(self.model.state_dict(), 'best_demand_model.pth')
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - "
                      f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        self.is_trained = True
        print(f"Training completed. Best validation loss: {best_val_loss:.4f}")
        
        return train_losses, val_losses
    
    def predict(self, start_date: datetime, num_days: int, 
                historical_data: Optional[pd.DataFrame] = None) -> Dict[datetime, Dict[str, int]]:
        """
        Predict nurse demand for future dates.
        
        Args:
            start_date: First date to predict
            num_days: Number of days to forecast
            historical_data: Recent historical data for context
        
        Returns:
            Dictionary mapping dates to demand per shift type
        """
        if not self.is_trained:
            # Return default demands if not trained
            return self._default_predictions(start_date, num_days)
        
        self.model.eval()
        predictions = {}
        
        with torch.no_grad():
            current_date = start_date
            
            for _ in range(num_days):
                # Prepare sequence
                sequence = []
                for i in range(self.sequence_length):
                    seq_date = current_date - timedelta(days=self.sequence_length - i)
                    features = self.prepare_features(seq_date, historical_data)
                    sequence.append(features)
                
                # Convert to tensor
                sequence_tensor = torch.FloatTensor([sequence]).to(self.device)
                
                # Predict
                output = self.model(sequence_tensor)
                output_np = output.cpu().numpy()
                
                # Inverse transform
                output_scaled = self.target_scaler.inverse_transform(output_np)[0]
                
                # Round to integers
                morning_demand = max(1, int(round(output_scaled[0])))
                afternoon_demand = max(1, int(round(output_scaled[1])))
                night_demand = max(1, int(round(output_scaled[2])))
                
                predictions[current_date] = {
                    'morning': morning_demand,
                    'afternoon': afternoon_demand,
                    'night': night_demand
                }
                
                current_date += timedelta(days=1)
        
        return predictions
    
    def _default_predictions(self, start_date: datetime, num_days: int) -> Dict[datetime, Dict[str, int]]:
        """Provide default predictions when model is not trained"""
        predictions = {}
        current_date = start_date
        
        for _ in range(num_days):
            # Simple heuristic: higher demand on weekdays, lower on weekends
            day_of_week = current_date.weekday()
            
            if day_of_week in [4, 5]:  # Friday, Saturday in Egypt
                base_demand = 3
            else:
                base_demand = 5
            
            predictions[current_date] = {
                'morning': base_demand + 1,
                'afternoon': base_demand,
                'night': base_demand - 1
            }
            
            current_date += timedelta(days=1)
        
        return predictions
    
    def save(self, path: str):
        """Save model and scalers"""
        checkpoint = {
            'model_state': self.model.state_dict(),
            'feature_scaler': self.feature_scaler,
            'target_scaler': self.target_scaler,
            'sequence_length': self.sequence_length,
            'is_trained': self.is_trained
        }
        torch.save(checkpoint, path)
        print(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model and scalers"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state'])
        self.feature_scaler = checkpoint['feature_scaler']
        self.target_scaler = checkpoint['target_scaler']
        self.sequence_length = checkpoint['sequence_length']
        self.is_trained = checkpoint['is_trained']
        print(f"Model loaded from {path}")


def generate_sample_data(num_days: int = 365) -> pd.DataFrame:
    """
    Generate sample historical data for testing.
    Simulates Egyptian hospital patterns.
    """
    dates = [datetime.now() - timedelta(days=i) for i in range(num_days, 0, -1)]
    data = []
    
    for date in dates:
        day_of_week = date.weekday()
        
        # Base demands
        if day_of_week in [4, 5]:  # Weekend in Egypt
            morning = np.random.randint(3, 5)
            afternoon = np.random.randint(2, 4)
            night = np.random.randint(2, 3)
        else:
            morning = np.random.randint(5, 8)
            afternoon = np.random.randint(4, 7)
            night = np.random.randint(3, 5)
        
        # Add seasonal variation
        month = date.month
        if month in [6, 7, 8]:  # Summer - potentially higher demand
            morning += 1
            afternoon += 1
        
        data.append({
            'date': date,
            'morning_demand': morning,
            'afternoon_demand': afternoon,
            'night_demand': night
        })
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    # Example usage
    print("Generating sample data...")
    historical_data = generate_sample_data(num_days=365)
    
    print("Initializing forecaster...")
    forecaster = DemandForecaster(sequence_length=14)
    
    print("Training model...")
    train_losses, val_losses = forecaster.train(
        historical_data, 
        epochs=50, 
        batch_size=32
    )
    
    print("\nMaking predictions for next 7 days...")
    predictions = forecaster.predict(
        start_date=datetime.now(),
        num_days=7,
        historical_data=historical_data
    )
    
    print("\nPredicted demands:")
    for date, demands in predictions.items():
        print(f"{date.date()}: {demands}")
    
    print("\nSaving model...")
    forecaster.save("demand_forecaster.pth")
