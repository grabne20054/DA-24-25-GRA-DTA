import os
import pickle
import mlflow
import mlflow.artifacts
from mlflow.tensorflow import load_model
from mlflow.tracking import MlflowClient
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from os import getenv

from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
from DataAnalysis.predictive.dependencies import OPTIONS, HORIZONS


class DataPredictor:

    def __init__(self, data_analysis: str):
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.data_analysis = data_analysis

    # ---------------------------------------------------------
    # LOAD BEST MODEL FROM MLFLOW
    # ---------------------------------------------------------
    def _get_best_model_id(self):
        client = MlflowClient(tracking_uri=getenv("MLFLOWURL"))
        mlflow.set_tracking_uri(getenv("MLFLOWURL"))

        experiment = client.get_experiment_by_name("GrowthEx")
        if experiment is None:
            raise Exception("Experiment not found")

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=f"attributes.run_name = '{self.data_analysis}'",
            run_view_type=mlflow.entities.ViewType.ACTIVE_ONLY,
            max_results=1,
            order_by=["metrics.val_mse ASC", "metrics.val_mae ASC"]
        )

        if not runs:
            raise Exception("No runs found")

        best_run = runs[0]
        return best_run.info.run_id, best_run.info.artifact_uri

    def _load_scaler(self, run_id: str, artifact_name: str):
        local_path = mlflow.artifacts.download_artifacts(
            run_id=run_id,
            artifact_path=f"model/{artifact_name}"
        )

        with open(local_path, "rb") as f:
            return pickle.load(f)

    def load_best_model(self):
        run_id, artifact_uri = self._get_best_model_id()

        model_uri = f"{artifact_uri}/model"
        self.model = load_model(model_uri)

        self.scaler_X = self._load_scaler(run_id, "scaler_X.pkl")
        self.scaler_y = self._load_scaler(run_id, "scaler_y.pkl")

    # ---------------------------------------------------------
    # DATA PREPARATION (SAME AS TRAINING)
    # ---------------------------------------------------------
    def _to_datetime_timestamp(self, date):
        if isinstance(date, str):
            if len(date) == 7:
                dt = datetime.strptime(date, "%Y-%m")
                dt = datetime(dt.year, dt.month, 1)
            elif len(date) == 4:
                dt = datetime.strptime(date, "%Y")
                dt = datetime(dt.year, 1, 1)
            else:
                dt = datetime.strptime(date, "%Y-%m-%d")
        else:
            dt = date

        return dt.timestamp()

    def _get_recent_data(self):
        if self.data_analysis == "CustomerGrowth":
            data = CustomerSignup().perform(
                last_days=OPTIONS["sequence_length"] + max(HORIZONS),
                showzeros=True,
                machine_learning=True
            )
        elif self.data_analysis == "OrdersGrowth":
            data = OrdersAmount().perform(
                last_days=OPTIONS["sequence_length"] + max(HORIZONS),
                showzeros=True,
                machine_learning=True
            )
        else:
            raise ValueError("Invalid analysis type")

        return data

    def _prepare_features(self, data_dict):
        timestamps = []
        values = []

        for k, v in data_dict["growth"].items():
            timestamps.append(self._to_datetime_timestamp(k))
            values.append(v)

        df = pd.DataFrame({
            "timestamp": timestamps,
            "growth": values
        })

        for i in range(1, OPTIONS["lag"] + 1):
            df[f"lag_{i}"] = df["growth"].shift(i)

        df["rolling_mean"] = df["growth"].rolling(
            window=OPTIONS["rolling_mean"]
        ).mean()

        df.dropna(inplace=True)

        X = df.drop(columns=["growth"]).values

        return X, df

    # ---------------------------------------------------------
    # PREDICT MULTI-HORIZON
    # ---------------------------------------------------------
    def predict(self):

        if self.model is None:
            self.load_best_model()

        raw_data = self._get_recent_data()
        X_raw, df = self._prepare_features(raw_data)

        X_scaled = self.scaler_X.transform(X_raw)

        seq_len = OPTIONS["sequence_length"]
        last_sequence = X_scaled[-seq_len:]
        last_sequence = last_sequence.reshape(1, seq_len, last_sequence.shape[1])

        y_pred_scaled = self.model.predict(last_sequence)

        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)

        y_pred = y_pred.flatten()

        last_timestamp = df["timestamp"].iloc[-1]
        last_date = datetime.fromtimestamp(last_timestamp)

        forecast = {}

        for horizon, value in zip(HORIZONS, y_pred):
            forecast_date = last_date + timedelta(days=horizon)
            forecast[str(forecast_date.date())] = float(value)

        return {"predictions": forecast}