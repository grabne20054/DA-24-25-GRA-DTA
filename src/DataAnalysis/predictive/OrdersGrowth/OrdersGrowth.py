from DataAnalysis.predictive.PredictiveAnalysis import PredictiveAnalysis
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
from sklearn.model_selection import train_test_split
import numpy as np
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

TF_ENABLE_ONEDNN_OPTS=0

load_dotenv()

class OrdersGrowth(PredictiveAnalysis):
    def __init__(self) -> None:
        self.orderAmount = OrdersAmount() 
    
    def collect(self):
        return self.orderAmount.perform()
    
    def provide_data_to_perform(self, lag, rolling_mean):
        X_train, X_test, y_train, y_test = self._train_test_split(lag, rolling_mean)
        X_train, X_test, scaler_x = self._normalize_X(X_train, X_test)
        y_train, y_test, scaler_y = self._normalize_y(y_train, y_test)
        X_train, y_train, X_test, y_test = self._create_sequences(X_train, y_train, X_test, y_test)

        return X_train, X_test, y_train, y_test, scaler_x, scaler_y

    def _prepare_data(self, lag, rolling_mean):
        data = self.collect()

        X = np.array([self._to_datetime_timestamp(key) for key in list(data['growth'].keys())])
        y = np.array([int(data['growth'][key]) for key in data['growth']])

        df = pd.DataFrame(y, columns=['growth'])
        df['timestamp'] = X
        
        # add lags
        for i in range(1, lag + 1):	
            df[f'lag_{i}'] = df['growth'].shift(i)
        
        # add rolling mean
        df['rolling_mean'] = df['growth'].rolling(window=rolling_mean).mean()

        df.dropna(inplace=True)
        
        X = np.array([self._to_datetime_timestamp(key) for key in list(data['growth'].keys())])
        y = np.array([int(data['growth'][key]) for key in data['growth']])


        day_of_dataset = datetime.fromtimestamp(X[0]).day
        month_of_dataset = datetime.fromtimestamp(X[0]).month
        year_of_dataset = datetime.fromtimestamp(X[0]).year
        X = np.column_stack((X, np.array([day_of_dataset for _ in range(len(X))]), 
                            np.array([month_of_dataset for _ in range(len(X))]), 
                            np.array([year_of_dataset for _ in range(len(X))])))
        
    

        X = df.drop(columns=['growth']).values

        y = df['growth'].values

        if X.size == 0 or y.size == 0:
            raise ValueError("Data preparation resulted in empty X or y arrays.")
        
        y = y.reshape(-1, 1)

        
        return X, y

    def _to_datetime_timestamp(self, date: str):
        dt = datetime.strptime(date, "%Y-%m-%d")
        return dt.timestamp()
    
    def _to_datetime_from_timestamp(self, timestamps):
        if isinstance(timestamps, np.ndarray):
            return [datetime.fromtimestamp(float(ts)) for ts in timestamps]
        else:
            return datetime.fromtimestamp(float(timestamps))
    
    def _train_test_split(self, lag, rolling_mean):
        X, y = self._prepare_data(lag, rolling_mean)
        return train_test_split(X, y, test_size=0.1, random_state=0, shuffle=False)
    
    def _normalize_X(self, X_train, X_test):
        if X_train.size == 0 or X_test.size == 0:
            raise ValueError("Training or testing data is empty.")
    
        # explain
        pipeline = Pipeline([
            ('robust_scaler', RobustScaler()),
            ('std_scaler', StandardScaler())
        ])

        X_train = pipeline.fit_transform(X_train)
        X_test = pipeline.transform(X_test)

        return X_train, X_test, pipeline
    
    def _normalize_y(self, y_train, y_test):
        if y_train.size == 0 or y_test.size == 0:
            raise ValueError("Training or testing data is empty.")
        
        pipeline = Pipeline([
            ('robust_scaler', RobustScaler()),
            ('std_scaler', StandardScaler())
        ])

        y_train = pipeline.fit_transform(y_train)
        y_test = pipeline.transform(y_test)

        return y_train, y_test, pipeline
    
    def _unscale_y(self, y, pipeline_y: Pipeline):
        #already in reverse order
        y_scaled = pipeline_y.inverse_transform(y)
        return y_scaled
    
    def _create_sequences(self, X_train, y_train, X_test, y_test):
        #fixed sequence length?
        #sequence_length = min(len(X_train), len(X_test)) - 1
        sequence_length = 10 # mock
        if sequence_length <= 0:
            raise ValueError(f"Invalid sequence_length: {sequence_length}. Must be > 0.")
        
        X_train_seq, y_train_seq = [], []
        for i in range(len(X_train) - sequence_length):
            X_train_seq.append(X_train[i:i + sequence_length])
            y_train_seq.append(y_train[i + sequence_length])
        
        X_test_seq, y_test_seq = [], []
        for i in range(len(X_test) - sequence_length):
            X_test_seq.append(X_test[i:i + sequence_length])
            y_test_seq.append(y_test[i + sequence_length])
        
        return np.array(X_train_seq), np.array(y_train_seq), np.array(X_test_seq), np.array(y_test_seq)

    def _shape_to_2D(self, X_train, X_test):
        if len(X_train.shape) == 3:
            X_train = X_train.reshape(X_train.shape[0], -1)
            X_test = X_test.reshape(X_test.shape[0], -1)
        return X_train, X_test


    def perform(self, num_units, dropout, learning_rate, epochs, l2_reg, lag, rolling_mean):

        X_train, X_test, y_train, y_test, scaler_x, scaler_y = self.provide_data_to_perform(lag, rolling_mean)

        model = Sequential([
            LSTM(num_units, input_shape=(X_train.shape[1], X_train.shape[2]), dropout=dropout),
            Dense(1)
        ])

        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=['mae'])

        ea = EarlyStopping(monitor='val_loss', verbose=1, patience=100)

        history = model.fit(X_train, y_train, epochs=epochs, validation_data=(X_test, y_test), batch_size=32 ,callbacks=[ea], verbose=1,)

        print("Training MSE:", history.history['loss'][-1])
        print("Validation MSE:", history.history['val_loss'][-1])
        print("Training MAE:", history.history['mae'][-1])
        print("Validation MAE:", history.history['val_mae'][-1])

        print(model.summary())
        
        y_pred = model.predict(X_test)
        y_pred_denormalized = self._unscale_y(y_pred, scaler_y)
        y_test = self._unscale_y(y_test, scaler_y)

        print("Test MSE:", mean_squared_error(y_test, y_pred_denormalized))
        print("Predicted Values:", y_pred_denormalized.flatten())
        print("True Values:", y_test)

        X_test_dates = self._to_datetime_from_timestamp(X_test[:, -1, 0])

        plt.figure(figsize=(12, 6))
        plt.scatter(X_test_dates, y_test, label='True', color='red')
        plt.plot(X_test_dates, y_test, label='True', color='red')
        plt.scatter(X_test_dates, y_pred_denormalized, label='Predicted', color='blue')
        plt.plot(X_test_dates, y_pred_denormalized, label='Predicted', color='blue')

        for i, txt in enumerate(range(len(X_test))):
            plt.annotate(txt, (X_test_dates[i], y_test[i]), textcoords="offset points", xytext=(0,10), ha='center', color='red')
            plt.annotate(txt, (X_test_dates[i], y_pred_denormalized[i]), textcoords="offset points", xytext=(0,10), ha='center', color='blue')

        plt.tight_layout()
        plt.show()

        return y_pred_denormalized

    def report(self):
        pass
