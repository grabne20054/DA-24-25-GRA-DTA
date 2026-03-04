import os
import sys
import logging
from os import getenv
from datetime import datetime, timedelta
from math import isnan
import pickle

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.pipeline import Pipeline
from typing import Literal

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping

import mlflow
from mlflow.keras import log_model

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from DataAnalysis.predictive.PredictiveAnalysis import PredictiveAnalysis
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.models.ModelParams import ModelParams
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.models.ModelData import ModelData

from DataAnalysis.predictive.dependencies import HORIZONS

# -------------------------------
# Logger setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("growth_model.log")
    ]
)
logger = logging.getLogger(__name__)

# -------------------------------
# Global constants
# -------------------------------
MODEL_DIR = '/models/'
TYPEOFGRAPH = "line"

NUM_UNITS = 120  # number of LSTM cells
DROPOUT = [0.1, 0.001]  # dropout rate for regularization
LEARNING_RATE = [1e-5, 1e-3]  # learning rates to try
EPOCHS = [100, 150]  # number of epochs for training
L2_REG = [0.0, 1e-6]  # L2 regularization strength

load_dotenv()

# -------------------------------
# GrowthModel class
# -------------------------------
class GrowthModel(PredictiveAnalysis):
    def __init__(self, data_analysis: str, growthtype: Literal['growth'], 
                 data_source: OrdersAmount | CustomerSignup) -> None:
        self.data_source = data_source
        self.growthtype = growthtype
        self.data_analysis = data_analysis
        self.setup_mlflow()
        self.data = self.collect()

    # -------------------------------
    # MLFlow setup
    # -------------------------------
    def setup_mlflow(self):
        try:
            mlflow.set_tracking_uri(getenv('MLFLOWURL'))
            if mlflow.set_experiment("GrowthEx") is None:
                mlflow.create_experiment("GrowthEx")
            logger.info("Successfully connected to MLFlow server")
        except Exception:
            logger.exception("Error connecting to MLFlow server")

    # -------------------------------
    # Data collection
    # -------------------------------
    def collect(self):
        try:
            return self.data_source.perform(showzeros=True, machine_learning=True)
        except Exception:
            logger.exception("Error in collect")
            return None

    # -------------------------------
    # Data preparation
    # -------------------------------
    def _to_datetime_timestamp(self, date):
        try:
            if isinstance(date, str):
                if len(date) == 7:
                    dt = datetime.strptime(date, "%Y-%m")
                    dt = datetime(dt.year, dt.month, 1)
                elif len(date) == 4:
                    dt = datetime.strptime(date, "%Y")
                    dt = datetime(dt.year, 1, 1)
                else:
                    dt = datetime.strptime(date, "%Y-%m-%d")
            elif isinstance(date, int):
                dt = datetime(date, 1, 1)
            elif isinstance(date, datetime):
                dt = date
            else:
                raise ValueError(f"Unsupported date format: {date}")
            return dt.timestamp()
        except Exception:
            logger.exception(f"Error converting date {date} to timestamp")
            raise

    def _prepare_data(self, lag, rolling_mean):
        if self.data is None:
            raise ValueError("Data collection failed. Please check the data source.")
        try:
            X = np.array([self._to_datetime_timestamp(k) for k in self.data[self.growthtype].keys()])
            y = np.array([int(self.data[self.growthtype][k]) for k in self.data[self.growthtype]])
        except Exception:
            logger.exception("Error converting data to arrays")
            return None, None

        try:
            df = pd.DataFrame(y, columns=[self.growthtype])
            df['timestamp'] = X

            # Add lag features
            lags = range(1, lag + 1)
            lag_cols = {}
            for i in lags:
                lag_cols[f'lag_{i}'] = df[self.growthtype].shift(i)

            lag_df = pd.DataFrame(lag_cols, index=df.index)
            df = pd.concat([df, lag_df], axis=1)

            # Add rolling mean
            df['rolling_mean'] = df[self.growthtype].rolling(window=rolling_mean).mean()
            df.dropna(inplace=True)
        except Exception:
            logger.exception("Error adding lags or rolling mean")
            return None, None

        X = df.drop(columns=[self.growthtype]).values
        y = df[self.growthtype].values.reshape(-1, 1)

        if X.size == 0 or y.size == 0:
            raise ValueError("Data preparation resulted in empty arrays.")

        return X, y

    # -------------------------------
    # Train-test split
    # -------------------------------
    def _train_test_split(self, lag, rolling_mean):
        X, y = self._prepare_data(lag, rolling_mean)
        return train_test_split(X, y, test_size=0.3, random_state=0, shuffle=False)

    # -------------------------------
    # Normalization
    # -------------------------------
    def _normalize(self, train, test):
        if len(train) == 0 or len(test) == 0:
            raise ValueError("Training or testing data is empty.")
        pipeline = Pipeline([
            ('robust_scaler', RobustScaler()),
            ('std_scaler', StandardScaler())
        ])
        train = pipeline.fit_transform(train)
        test = pipeline.transform(test)
        return train, test, pipeline


    # -------------------------------
    # Sequence creation
    # -------------------------------
    def _create_sequences(self, X_train, y_train, X_test, y_test, sequence_length, horizons=HORIZONS):
        if sequence_length <= 0:
            raise ValueError("sequence_length must be > 0")

        X_train_seq, y_train_seq = [], []
        for i in range(len(X_train) - sequence_length - max(horizons) + 1):
            X_train_seq.append(X_train[i:i + sequence_length])
            y_train_seq.append([y_train[i + sequence_length + h - 1] for h in horizons])

        X_test_seq, y_test_seq = [], []
        for i in range(len(X_test) - sequence_length - max(horizons) + 1):
            X_test_seq.append(X_test[i:i + sequence_length])
            y_test_seq.append([y_test[i + sequence_length + h - 1] for h in horizons])

        return (np.array(X_train_seq), np.array(y_train_seq),
                np.array(X_test_seq), np.array(y_test_seq))

    # -------------------------------
    # Pipeline for data
    # -------------------------------
    def provide_data_to_perform(self, lag, rolling_mean, sequence_length):
        X_train, X_test, y_train, y_test = self._train_test_split(lag, rolling_mean)
        if X_train is None or X_test is None or len(X_train) == 0 or len(X_test) == 0:
            raise ValueError("Not enough data.")
        X_train, X_test, scaler_X = self._normalize(X_train, X_test)
        y_train, y_test, scaler_y = self._normalize(y_train, y_test)

        # create sequences (will return arrays for train/test sequences)
        X_train_seq, y_train_seq, X_test_seq, y_test_seq = self._create_sequences(
            X_train, y_train, X_test, y_test, sequence_length
        )

        # Ensure sequences have shape (samples, timesteps, features) for LSTM
        if X_train_seq.ndim == 2:
            X_train_seq = X_train_seq.reshape((X_train_seq.shape[0], sequence_length, -1))
        if X_test_seq.ndim == 2:
            X_test_seq = X_test_seq.reshape((X_test_seq.shape[0], sequence_length, -1))

        # Ensure targets are 2D (samples, 1)
        if y_train_seq.ndim == 1:
            y_train_seq = y_train_seq.reshape(-1, 1)
        if y_test_seq.ndim == 1:
            y_test_seq = y_test_seq.reshape(-1, 1)

        return X_train_seq, X_test_seq, y_train_seq, y_test_seq, scaler_X, scaler_y

    # -------------------------------
    # Training and hyperparameter search
    # -------------------------------
    def find_best_params(self, options: dict):
        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self.provide_data_to_perform(
                lag=options["lag"],
                rolling_mean=options["rolling_mean"],
                sequence_length=options["sequence_length"]
            )
        
        modeldata = ModelData(
            lag=options["lag"],
            rolling_mean=options["rolling_mean"],
            sequence_length=options["sequence_length"],
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            scaler_X=scaler_X,
            scaler_y=scaler_y
        )

        params = self.run(modeldata)
        self.save_best_model(params)

        return None

    def run(self, modeldata: ModelData) -> ModelParams:

        results = {}
        for dropout in DROPOUT:
            for learning_rate in LEARNING_RATE:
                for epoch in EPOCHS:
                    for l2_reg in L2_REG:
                        logger.info(f"Running with {NUM_UNITS} LSTM cells, dropout={dropout}, lr={learning_rate}, l2={l2_reg}")

                        model = Sequential()
                        model.add(LSTM(NUM_UNITS, dropout=dropout, return_sequences=False, input_shape=(modeldata.X_train.shape[1], modeldata.X_train.shape[2]), kernel_regularizer=l2(l2_reg)))
                        model.add(Dense(len(HORIZONS)))
                        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=['mae'])
                        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
                        history = model.fit(modeldata.X_train, modeldata.y_train, epochs=epoch, batch_size=32, validation_data=(modeldata.X_test, modeldata.y_test), verbose=1, callbacks=[early_stopping])

                        best_epoch = np.argmin(history.history['val_loss'])
                        train_mse = history.history['loss'][best_epoch]
                        val_mse = history.history['val_loss'][best_epoch]
                        train_mae = history.history['mae'][best_epoch]
                        val_mae = history.history['val_mae'][best_epoch]

                        results[(NUM_UNITS, dropout, learning_rate, best_epoch, l2_reg, model)] = {
                            'train_mse': train_mse,
                            'val_mse': val_mse,
                            'train_mae': train_mae,
                            'val_mae': val_mae
                        }

                        logger.info(f"Train MSE={train_mse}, Val MSE={val_mse}, Train MAE={train_mae}, Val MAE={val_mae}")

        val_results = {key: results[key]['val_mse'] for key in results.keys()}
        num_cells, dropout_rate, lr, num_epochs, l2_reg, model = min(val_results, key=val_results.get)
        logger.info(f"Best parameters: {num_cells} cells, {num_epochs} epochs, dropout={dropout_rate}, lr={lr}, l2={l2_reg}")
        
        return ModelParams(
            run_name=self.data_analysis,
            num_units=num_cells,
            dropout=dropout_rate,
            learning_rate=lr,
            epoch=num_epochs,
            l2_reg=l2_reg,
            train_mse=results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['train_mse'],
            val_mse=results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['val_mse'],
            train_mae=results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['train_mae'],
            val_mae=results[(num_cells, dropout_rate, lr, num_epochs, l2_reg, model)]['val_mae'],
            model=model,
            input_example=modeldata.X_train.reshape(modeldata.X_train.shape[0], -1),
            scaler_y=modeldata.scaler_y,
            scaler_X=modeldata.scaler_X,
            lag=modeldata.lag,
            rolling_mean=modeldata.rolling_mean,
            sequence_length=modeldata.sequence_length
        )

    # -------------------------------
    # Save model and scalers
    # -------------------------------
    def save_best_model(self, params: ModelParams):
        try:
            mlflow.start_run(run_name=params.run_name)
            mlflow.log_param('num_units', params.num_units)
            mlflow.log_param('dropout', params.dropout)
            mlflow.log_param('learning_rate', params.learning_rate)
            mlflow.log_param('epoch', params.epoch)
            mlflow.log_param('l2_reg', params.l2_reg)
            mlflow.log_param('lag', params.lag)
            mlflow.log_param('rolling_mean', params.rolling_mean)
            mlflow.log_param('sequence_length', params.sequence_length)

            log_model(params.model, 'model') # TODO input example and signature
            self._save_scaler(params.scaler_y, "scaler_y.pkl")
            self._save_scaler(params.scaler_X, "scaler_X.pkl")

            mlflow.log_metric('train_mse', params.train_mse)
            mlflow.log_metric('val_mse', params.val_mse)
            mlflow.log_metric('train_mae', params.train_mae)
            mlflow.log_metric('val_mae', params.val_mae)

            logger.info(f"Run {params.run_name} saved successfully")
        except Exception:
            logger.exception("Error saving model to MLFlow")
        finally:
            mlflow.end_run()

    # -------------------------------
    # Utility methods
    # -------------------------------
    def _save_scaler(self, scaler, scaler_path):
        with open(scaler_path, "wb") as file:
            pickle.dump(scaler, file)
        mlflow.log_artifact(scaler_path, artifact_path="model")
        logger.info(f"Scaler saved to {scaler_path}")

    def perform(self, options: dict, model):
        self.data_source = model

        self.find_best_params(options)

    def report(self):
        pass
    
    def is3Dim(self, data: np.ndarray):
        if data.ndim != 3:
            return False
        return True 
