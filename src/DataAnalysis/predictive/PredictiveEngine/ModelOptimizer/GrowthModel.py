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
from models.ModelParams import ModelParams

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
DROPOUT = 0.1    # dropout rate for regularization
LEARNING_RATE = 1e-5
EPOCHS = 100
L2_REG = 1e-4

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
    def collect(self, month: bool = False, year: bool = False):
        try:
            showzeros = True
            if year:
                return self.data_source.perform(year=year, showzeros=showzeros)
            elif month:
                return self.data_source.perform(month=month, showzeros=showzeros)
            else:
                return self.data_source.perform(showzeros=showzeros)
        except Exception:
            logger.exception("Error in collect")
            return None

    # -------------------------------
    # Data preparation
    # -------------------------------
    def _to_datetime_timestamp(self, date):
        logger.debug(f"Converting date {type(date)} {date} to timestamp")
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

    def _prepare_data(self, lag, rolling_mean, month: bool = False, year: bool = False):
        data = self.collect(month, year)
        if data is None:
            raise ValueError("Data collection failed. Please check the data source.")
        logger.info(f"Collected data: {data}")
        try:
            X = np.array([self._to_datetime_timestamp(k) for k in data[self.growthtype].keys()])
            y = np.array([int(data[self.growthtype][k]) for k in data[self.growthtype]])
        except Exception:
            logger.exception("Error converting data to arrays")
            return None, None

        try:
            df = pd.DataFrame(y, columns=[self.growthtype])
            df['timestamp'] = X

            # Add lag features
            for i in range(1, lag + 1):
                df[f'lag_{i}'] = df[self.growthtype].shift(i)

            # Add rolling mean
            df['rolling_mean'] = df[self.growthtype].rolling(window=rolling_mean).mean()
            df.dropna(inplace=True)
        except Exception:
            logger.exception("Error adding lags or rolling mean")
            return None, None

        X = df.drop(columns=[self.growthtype]).values
        y = df[self.growthtype].values.reshape(-1, 1)
        logger.info(f"Prepared data with shape X: {X.shape}, y: {y.shape}")
        logger.info(f"Prepared data example: {X}, {y}")

        if X.size == 0 or y.size == 0:
            raise ValueError("Data preparation resulted in empty arrays.")

        return X, y

    # -------------------------------
    # Train-test split
    # -------------------------------
    def _train_test_split(self, lag, rolling_mean, month: bool = False, year: bool = False):
        X, y = self._prepare_data(lag, rolling_mean, month, year)
        logger.info(f"train test split {train_test_split(X, y, test_size=0.3, random_state=0, shuffle=False)}")
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

    def _unscale_y(self, y, pipeline_y: Pipeline):
        return pipeline_y.inverse_transform(y)

    # -------------------------------
    # Sequence creation
    # -------------------------------
    def _create_sequences(self, X_train, y_train, X_test, y_test, sequence_length):
        if sequence_length <= 0:
            raise ValueError("sequence_length must be > 0")

        X_train_seq, y_train_seq = [], []
        for i in range(len(X_train) - sequence_length):
            X_train_seq.append(X_train[i:i + sequence_length])
            y_train_seq.append(y_train[i + sequence_length])

        X_test_seq, y_test_seq = [], []
        for i in range(len(X_test) - sequence_length):
            X_test_seq.append(X_test[i:i + sequence_length])
            y_test_seq.append(y_test[i + sequence_length])

        logger.debug(f"Created {len(X_train_seq)} training sequences")
        return (np.array(X_train_seq), np.array(y_train_seq),
                np.array(X_test_seq), np.array(y_test_seq))

    # -------------------------------
    # Pipeline for data
    # -------------------------------
    def provide_data_to_perform(self, lag, rolling_mean, sequence_length, month=False, year=False):
        X_train, X_test, y_train, y_test = self._train_test_split(lag, rolling_mean, month, year)
        if X_train is None or X_test is None or len(X_train) == 0 or len(X_test) == 0:
            raise ValueError("Not enough data.")
        X_train, X_test, scaler_X = self._normalize(X_train, X_test)
        y_train, y_test, scaler_y = self._normalize(y_train, y_test)

        # create sequences (will return arrays for train/test sequences)
        X_train_seq, y_train_seq, X_test_seq, y_test_seq = self._create_sequences(
            X_train, y_train, X_test, y_test, sequence_length
        )

        logger.info(f"Final data shapes - X_train: {X_train_seq.shape}, y_train: {y_train_seq.shape}, X_test: {X_test_seq.shape}, y_test: {y_test_seq.shape}")
        logger.info(f"Final data examples - X_train: {X_train_seq}, y_train: {y_train_seq}, X_test: {X_test_seq}, y_test: {y_test_seq}")

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
    def find_best_params(self, lag, rolling_mean, sequence_length, month=False, year=False):
        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self.provide_data_to_perform(
            lag, rolling_mean, sequence_length, month, year)

        results = {}
        for num_units in [NUM_UNITS]:
            for dropout in [DROPOUT]:
                for learning_rate in [LEARNING_RATE]:
                    for epoch in [EPOCHS]:
                        for l2_reg in [L2_REG]:
                            logger.info(f"Running with {num_units} LSTM cells, dropout={dropout}, lr={learning_rate}, l2={l2_reg}")
                            logger.info(f"Training data shape: {X_train.shape}, {y_train.shape}")
                            logger.info(f"Training data example: {X_train}, {y_train}")
                            model = Sequential([
                                LSTM(num_units, input_shape=(X_train.shape[1], X_train.shape[2]), dropout=dropout, kernel_regularizer=l2(l2_reg)),
                                Dense(1)
                            ])
                            model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=['mae'])
                            history = model.fit(X_train, y_train, epochs=epoch, batch_size=32, validation_data=(X_test, y_test), verbose=1)

                            best_epoch = np.argmin(history.history['val_loss'])
                            train_mse = history.history['loss'][best_epoch]
                            val_mse = history.history['val_loss'][best_epoch]
                            train_mae = history.history['mae'][best_epoch]
                            val_mae = history.history['val_mae'][best_epoch]

                            results[(num_units, dropout, learning_rate, best_epoch, l2_reg, model)] = {
                                'train_mse': train_mse,
                                'val_mse': val_mse,
                                'train_mae': train_mae,
                                'val_mae': val_mae
                            }

                            logger.info(f"Train MSE={train_mse}, Val MSE={val_mse}, Train MAE={train_mae}, Val MAE={val_mae}")

        val_results = {key: results[key]['val_mse'] for key in results.keys()}
        num_cells, dropout_rate, lr, num_epochs, l2_reg, model = min(val_results, key=val_results.get)
        logger.info(f"Best parameters: {num_cells} cells, {num_epochs} epochs, dropout={dropout_rate}, lr={lr}, l2={l2_reg}")

        params = ModelParams(
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
            input_example=X_train.reshape(X_train.shape[0], -1),
            scaler_y=scaler_y,
            scaler_X=scaler_X,
            lag=lag,
            rolling_mean=rolling_mean,
            sequence_length=sequence_length
        )

        self.save_best_model(params)
        return num_epochs, num_epochs, lr, dropout_rate

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
    # Prediction
    # -------------------------------
    def predict(self, X_test_raw, model, scaler_y, scaler_X, lag, rolling_mean, sequence_length, option: str):
        X_test, _ = self._normalize_X_test(X_test_raw, scaler_X)
        X_test_seq = [X_test[i:i + sequence_length] for i in range(len(X_test) - sequence_length)]
        X_test = np.array(X_test_seq)
        y_pred = model.predict(X_test)
        y_pred = self._unscale_y(y_pred, scaler_y)
        y_pred_list = [y[0] for y in y_pred]

        if option == "one_day":
            pred_list = {(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"): y_pred_list[0]}
        elif option == "seven_days":
            pred_list = {(datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"): y_pred_list[i] for i in range(7)}
        elif option == "month":
            pred_list = {datetime.now().strftime("%Y-%m"): y_pred_list[0]}
        elif option == "year":
            pred_list = {datetime.now().year: y_pred_list[0]}

        return {"predictions": pred_list, "typeofgraph": TYPEOFGRAPH}

    # -------------------------------
    # Utility methods
    # -------------------------------
    def _save_scaler(self, scaler, scaler_path):
        with open(scaler_path, "wb") as file:
            pickle.dump(scaler, file)
        mlflow.log_artifact(scaler_path, artifact_path="model")
        logger.info(f"Scaler saved to {scaler_path}")

    def _normalize_X_test(self, X_test, pipeline: Pipeline):
        if len(X_test) == 0:
            raise ValueError("Testing data is empty.")
        X_test = pipeline.transform(pd.DataFrame(X_test))
        return X_test, pipeline

    def perform(self, lag, rolling_mean, sequence_length, month, year):
        self.find_best_params(lag, rolling_mean, sequence_length, month, year)

    def report(self):
        pass