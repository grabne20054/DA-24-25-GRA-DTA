from predictive.PredictiveAnalysis import PredictiveAnalysis
from descriptive.CustomerSignup import CustomerSignup
from sklearn.model_selection import train_test_split
import numpy as np
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import mlflow

load_dotenv()

class CustomerGrowth(PredictiveAnalysis):
    def __init__(self) -> None:
        self.customerSignup = CustomerSignup() 
    
    def collect(self):
        return self.customerSignup.perform()
    
    def provide_data_to_perform(self):
        X_train, X_test, y_train, y_test = self._train_test_split()
        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self._normalize_data(X_train, X_test, y_train, y_test)

        X_train, X_test = self._shape_to_3D(X_train, X_test)

        return X_train, X_test, y_train, y_test, scaler_X, scaler_y

    def _prepare_data(self):
        data = self.collect()
        X = np.array([self._to_datetime_timestamp(key) for key in list(data['cumulative_growth'].keys())])
        y = np.array([int(data['cumulative_growth'][key]) for key in data['cumulative_growth']])
        day_of_week = [datetime.fromtimestamp(date).weekday() for date in X]
        month_of_year = [datetime.fromtimestamp(date).month for date in X]

        X = np.column_stack((X, day_of_week, month_of_year))
        y = y.reshape(-1, 1)

        if X.size == 0 or y.size == 0:
            raise ValueError("Data preparation resulted in empty X or y arrays.")

        return X, y

    def _to_datetime_timestamp(self, date: str):
        dt = datetime.strptime(date, "%Y-%m-%d")
        return dt.timestamp()
    
    def _to_datetime_from_timestamp(self, timestamps):
        if isinstance(timestamps, np.ndarray):
            return [datetime.fromtimestamp(float(ts)) for ts in timestamps]
        else:
            return datetime.fromtimestamp(float(timestamps))
    
    def _train_test_split(self, sequence_length=300):
        X, y = self._prepare_data()
        X_seq, y_seq = self._create_sequences(X, y, sequence_length)
        return train_test_split(X_seq, y_seq, test_size=0.2, random_state=0, shuffle=False)
    
    def _normalize_data(self, X_train, X_test, y_train, y_test):
        if X_train.size == 0 or X_test.size == 0:
            raise ValueError("Training or testing data is empty.")
        
        X_train, X_test = self._shape_to_2D(X_train, X_test)

        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()

        X_train = scaler_X.fit_transform(X_train)
        X_test = scaler_X.transform(X_test)
        y_train = scaler_y.fit_transform(y_train)
        y_test = scaler_y.transform(y_test)

        return X_train, X_test, y_train, y_test, scaler_X, scaler_y
    
    def _denormalize_data(self, y_pred, scaler_y):
        return scaler_y.inverse_transform(y_pred)
    
    def _create_sequences(self, X, y, sequence_length):
        if sequence_length <= 0 or sequence_length > len(X):
            raise ValueError(f"Invalid sequence_length: {sequence_length}. Must be > 0 and <= {len(X)}.")
        X_seq, y_seq = [], []
        for i in range(len(X) - sequence_length):
            X_seq.append(X[i:i + sequence_length])
            y_seq.append(y[i + sequence_length])
        return np.array(X_seq), np.array(y_seq)

    def _shape_to_2D(self, X_train, X_test):
        if len(X_train.shape) == 3:
            X_train = X_train.reshape(X_train.shape[0], -1)
            X_test = X_test.reshape(X_test.shape[0], -1)
        return X_train, X_test
    
    def _shape_to_3D(self, X_train, X_test):
        if len(X_train.shape) == 2:
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
            X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        return X_train, X_test

    def perform(self, num_units, dropout, learning_rate, epochs):

        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self.provide_data_to_perform()

        model = Sequential([
                        LSTM(num_units, input_shape=(X_train.shape[1], X_train.shape[2]), kernel_regularizer=tf.keras.regularizers.l2(0.01), dropout=dropout  ),
                        Dense(1)
                    ])
        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=['mse'])

        history = model.fit(X_train, y_train, epochs=epochs, batch_size=64,  validation_data=(X_test, y_test), verbose=1)
        

        print(model.summary())
        y_pred = model.predict(X_test)
        y_pred_denormalized = self._denormalize_data(y_pred, scaler_y)
        y_test_denormalized = self._denormalize_data(y_test, scaler_y)

        print("Test MSE:", mean_squared_error(y_test_denormalized, y_pred_denormalized))
        print("Predicted Values:", y_pred_denormalized.flatten())
        print("True Values:", y_test_denormalized.flatten())
        
        X_test_dates = [self._to_datetime_from_timestamp(ts[0]) for ts in X_test[:, 0, :]]

        plt.plot(X_test_dates, y_test_denormalized, label='True')
        plt.plot(X_test_dates, y_pred_denormalized, label='Predicted')
        plt.legend()
        plt.show()

        return y_pred_denormalized

    def report(self):
        pass