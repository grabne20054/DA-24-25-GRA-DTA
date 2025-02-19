import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from DataAnalysis.predictive.PredictiveAnalysis import PredictiveAnalysis
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from sklearn.model_selection import train_test_split
import numpy as np
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import RobustScaler, StandardScaler
from typing import Literal
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.keras import log_model
from math import isnan
import pickle

MODEL_DIR = '/models/'

load_dotenv()

class GrowthModel(PredictiveAnalysis):
    def __init__(self, data_analysis: str, growthtype: Literal['growth', 'cumulative_growth'], data_source: OrdersAmount | CustomerSignup ) -> None:
        self.data_source = data_source
        self.growthtype = growthtype
        self.data_analysis = data_analysis
        self.setup_mlflow()

    def setup_mlflow(self):
        mlflow.set_tracking_uri(getenv('MLFLOWURL'))
        if mlflow.set_experiment("GrowthEx") is None:
            mlflow.create_experiment("GrowthEx")
        print('Successfully connected to MLFlow server')
    
    def collect(self, month: bool = False, year: bool = False):
        try:
            showzeros = False
            if self.growthtype == 'growth':
                print(self.growthtype, showzeros)
                showzeros = True
            if year:
                return self.data_source.perform(year=year, showzeros=showzeros)
            elif month:
                return self.data_source.perform(month=month, showzeros=showzeros)
            else:
                return self.data_source.perform(showzeros=showzeros)
        except Exception as e:
            print(f"Error in collect: {e}")
            return None
        
    def provide_data_to_perform(self, lag, rolling_mean, sequence_length, month: bool = False, year: bool = False):
        X_train, X_test, y_train, y_test = self._train_test_split(lag, rolling_mean, month, year)
        X_train, X_test, scaler_x = self._normalize_X(X_train, X_test)
        y_train, y_test, scaler_y = self._normalize_y(y_train, y_test)
        X_train, y_train, X_test, y_test = self._create_sequences(X_train, y_train, X_test, y_test, sequence_length)

        return X_train, X_test, y_train, y_test, scaler_x, scaler_y

    def _prepare_data(self, lag, rolling_mean, month: bool = False, year: bool = False):
        data = self.collect(month, year)

        if data is None:
            raise ValueError("Data collection failed. Please check the data source and try again.")

        try:
            X = np.array([self._to_datetime_timestamp(key) for key in list(data[self.growthtype].keys())])
            y = np.array([int(data[self.growthtype][key]) for key in data[self.growthtype]])
        except Exception as e:
            print(f"Error in Data Preparation: {e}")
            return None, None
        
    
        try:
            df = pd.DataFrame(y, columns=[self.growthtype])
            df['timestamp'] = X

            # add lags
            for i in range(1, lag + 1):	
                df[f'lag_{i}'] = df[self.growthtype].shift(i)
            
            # add rolling mean
            df['rolling_mean'] = df[self.growthtype].rolling(window=rolling_mean).mean()
            df.dropna(inplace=True)
        
        except Exception as e:
            print(f"Error in adding lags, and rolling mean: {e}")
            return None, None
        
        X = df.drop(columns=[self.growthtype]).values

        y = df[self.growthtype].values

        if X.size == 0 or y.size == 0:
            raise ValueError("Data preparation resulted in empty X or y arrays.")
        
        y = y.reshape(-1, 1)

        
        return X, y

    def _to_datetime_timestamp(self, date):
        if isinstance(date, str):
            if len(date) == 2:
                dt = datetime.strptime(date, "%m")
                dt = datetime(datetime.now().year, dt.month, 1)
            elif len(date) == 4:
                dt = datetime.strptime(date, "%Y")
                dt = datetime(dt.year, 1, 1)
            else:
                dt = datetime.strptime(date, "%Y-%m-%d")
        else:
            dt = date

        return dt.timestamp()
    
    def _to_datetime_from_timestamp(self, timestamps):
        if isinstance(timestamps, np.ndarray):
            return [datetime.fromtimestamp(float(ts)) for ts in timestamps]
        else:
            return datetime.fromtimestamp(float(timestamps))
    
    def _train_test_split(self, lag, rolling_mean, month: bool = False, year: bool = False):
        X, y = self._prepare_data(lag, rolling_mean, month, year)
        return train_test_split(X, y, test_size=0.5, random_state=0, shuffle=False)
    
    def _normalize_X(self, X_train, X_test):
        if len(X_train) == 0 or len(X_test) == 0:
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
    
    def _create_sequences(self, X_train, y_train, X_test, y_test, sequence_length):
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


    def find_best_params(self, lag, rolling_mean, sequence_length, month: bool = False, year: bool = False):
        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self.provide_data_to_perform(lag, rolling_mean, sequence_length, month, year)

        results = {}
        for num_units in [120]:
            for dropout in [0.1]:
                for learning_rate in [1e-5]:
                    for epoch in [50]:
                        for l2_reg in [1e-4]:

                            print('Running with', num_units, 
                                'LSTM cells, dropout =', dropout, 
                                'and learning rate =', learning_rate,
                                'and l2 reg=', l2_reg, '...')
                            
                            model = Sequential([
                                LSTM(num_units, input_shape=(X_train.shape[1], X_train.shape[2]), dropout=dropout, kernel_regularizer=l2(l2_reg)),
                                Dense(1)
                            ])
                            model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=[ 'mae'])

                            history = model.fit(X_train, y_train, epochs=epoch, batch_size=32,  validation_data=(X_test, y_test), verbose=1)
                           
                            num_epochs = len(history.history['val_loss'])
                            best_epoch = np.argmin(history.history['val_loss'])

                            train_mse = history.history['loss'][best_epoch]
                            val_mse = history.history['val_loss'][best_epoch] 
                            train_mae = history.history['mae'][best_epoch]
                            val_mae = history.history['val_mae'][best_epoch]

                            results[(num_units, dropout, learning_rate, best_epoch, l2_reg, model)] = {'train_mse': train_mse, 
                                                                                    'val_mse': val_mse, 'train_mae': train_mae, 'val_mae': val_mae,}                                                                                          
                            print('Train MSE =', train_mse, ', Validation MSE =', val_mse, ', Train MAE =', train_mae, ', Validation MAE =', val_mae)        
                            print('+----------------------------------------------------------------------+')

        val_results = {key: results[key]['val_mse'] for key in results.keys()}
        num_cells, dropout_rate, lr, num_epochs, l2_reg, model = min(val_results, key=val_results.get)
        print('Best parameters:', num_cells, 
                'LSTM cells, training for', num_epochs, 
                'epochs with dropout =', dropout_rate, 
                'and learning rate =', lr
                , 'and l2 reg=', l2_reg)
        
        
        if not isnan(results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['val_mse']):
        
            self.save_best_model(self.data_analysis, num_cells, dropout_rate, lr, num_epochs, l2_reg ,results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['train_mse'], results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['val_mse'], results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['train_mae'], results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['val_mae'], model, X_train, scaler_y, scaler_X, lag, rolling_mean, sequence_length)
        else:
            print('Invalid results. Skipping...')
        



        return num_epochs, best_epoch, learning_rate, dropout_rate
    
    def save_best_model(self, run_name, num_units, dropout, learning_rate, epoch, l2_reg ,train_mse, val_mse, train_mae, val_mae, model, input_example, scaler_y, scaler_X, lag, rolling_mean, sequence_length):
        mlflow.start_run(run_name=run_name)
        mlflow.log_param('num_units', num_units)
        mlflow.log_param('dropout', dropout)
        mlflow.log_param('learning_rate', learning_rate)
        mlflow.log_param('epoch', epoch)
        mlflow.log_param('l2_reg', l2_reg)
        mlflow.log_param('lag', lag)
        mlflow.log_param('rolling_mean', rolling_mean)
        mlflow.log_param('sequence_length', sequence_length)

        log_model(model, 'model', input_example=input_example)

        self._save_scaler(scaler_y, scaler_path="scaler_y.pkl")
        self._save_scaler(scaler_X, scaler_path="scaler_X.pkl")


        mlflow.log_metric('train_mse', train_mse)
        mlflow.log_metric('val_mse', val_mse)
        mlflow.log_metric('train_mae', train_mae)
        mlflow.log_metric('val_mae', val_mae)

        print('Run', run_name, 'saved successfully')
        print('+----------------------------------------------------------------------+')

        mlflow.end_run()

    def perform(self, lag, rolling_mean, sequence_length, month: bool = False, year: bool = False):
            self.find_best_params(lag=lag, rolling_mean=rolling_mean, sequence_length=sequence_length, month=month, year=year)

    # TODO scaler log, refactor...
    def _normalize_X_test(self, X_test, pipeline : Pipeline):
        if len(X_test) == 0:
            raise ValueError("Training or testing data is empty.")
    
        X_test = pipeline.fit_transform(pd.DataFrame(X_test))

        return X_test, pipeline


    def predict(self, X_test_raw, model, scaler_y, scaler_X, lag, rolling_mean, sequence_length, option:str):
        X_test, _ = self._normalize_X_test(X_test_raw, scaler_X)
        X_test_seq = []
        for i in range(len(X_test) - sequence_length):
            X_test_seq.append(X_test[i:i + sequence_length])

        X_test = np.array(X_test_seq)
        y_pred = model.predict(X_test)

        y_pred = self._unscale_y(y_pred, scaler_y)

        y_pred_list = y_pred.tolist()

        for i in range(len(y_pred_list)):
            y_pred_list[i] = y_pred_list[i][0]

        if option == "one_day":
            return {(datetime.now() + timedelta(days=1)).isoformat().split("T")[0] :  y_pred_list[0]}
        elif option == "seven_days":
            res = {}
            seven_days = [datetime.now() + timedelta(days=i+1) for i in range(7)]
            print(seven_days)
            for i in seven_days:
                res[i.isoformat().split("T")[0]] = y_pred_list[seven_days.index(i)]
            return res
        elif option == "month":
            return {datetime.now().month :  y_pred_list[0]}
        elif option == "year":
            return {datetime.now().year :  y_pred_list[0]}
        
            

    def _save_scaler(self, scaler, scaler_path):
        with open(scaler_path, "wb") as file:
            pickle.dump(scaler, file)
        mlflow.log_artifact(scaler_path, artifact_path="model")


    def report():
        pass


if __name__ == "__main__":
    customerGrowth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
    customerGrowth.perform()
