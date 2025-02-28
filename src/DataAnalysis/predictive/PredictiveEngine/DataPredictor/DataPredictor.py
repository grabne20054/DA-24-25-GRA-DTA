import mlflow.artifacts
from mlflow.tensorflow import load_model
from mlflow.tracking import MlflowClient
from datetime import datetime, timedelta
from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.GrowthModel import GrowthModel
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup
from DataAnalysis.descriptive.OrdersAmount import OrdersAmount
import numpy as np
import pandas as pd
import pickle
import os

from DataAnalysis.predictive.PredictiveEngine.ModelOptimizer.ModelOptimizer import OPTIONS

import mlflow
from os import getenv

class DataPredictor:

    def __init__(self, data_analysis:str):
        self.model = None
        self.scaler_y = None
        self.scaler_X = None
        self.data_analysis = data_analysis

    def _get_best_model_id(self, data_analysis:str, option:str) -> str:
        try:
            client = MlflowClient(tracking_uri=getenv("MLFLOWURL"))
            mlflow.set_tracking_uri(getenv("MLFLOWURL"))
            experiment = client.get_experiment_by_name("GrowthEx")

            if experiment is None:
                raise Exception('Experiment not found')
            else: 
                runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"""
                attributes.run_name = '{data_analysis}' 
                AND params.`lag` = '{OPTIONS[option]['lag']}' 
                AND params.`sequence_length` = '{OPTIONS[option]['sequence_lenght']}' 
                AND params.`rolling_mean` = '{OPTIONS[option]['rolling_mean']}'
                """,
                run_view_type=mlflow.entities.ViewType.ACTIVE_ONLY,
                max_results=1,
                order_by=["metrics.train_mse DESC", "metrics.train_mae DESC"]
            )

            if not runs:
                raise Exception('No runs found for the given parameters')

            best_run = runs[0]
                
            return best_run.info.run_id, best_run.info.artifact_uri
        except Exception as e:
            raise e

    def _getScalerOfModel(self, run_id: str, artifact_path: str = "model/scaler.pkl") -> None:
        try:
            scaler_local = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path=artifact_path)

            if not os.path.exists(scaler_local):
                raise FileNotFoundError(f"Scaler file not found at {scaler_local}")

            with open(scaler_local, "rb") as f:
                scaler = pickle.load(f)

            if artifact_path == "model/scaler_y.pkl":
                self.scaler_y = scaler
            elif artifact_path == "model/scaler_X.pkl":
                self.scaler_X = scaler

        except Exception as e:
            raise Exception(f"Failed to retrieve scaler: {e}")

            

    def loadBestModel(self, data_analysis:str, option:str):
        best_model_id, artifact_uri = self._get_best_model_id(data_analysis, option)
        model_url = f"{artifact_uri}/model"
        self.model = load_model(model_url)
        self._getScalerOfModel(best_model_id, "model/scaler_y.pkl")
        self._getScalerOfModel(best_model_id, "model/scaler_X.pkl")

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
    
    def predict(self, data_analysis:str, option:str):
        self.loadBestModel(data_analysis, option)
        if self.model is None:
            raise Exception("Model not loaded")
        if self.scaler_X is None:
            raise Exception("Scaler X not loaded")
        if self.scaler_y is None:
            raise Exception("Scaler y not loaded")

        if data_analysis == "CumulativeCustomerGrowth":
            growth = GrowthModel("CumulativeCustomerGrowth", "cumulative_growth", data_source=CustomerSignup())
            X_test = self._getHistoricalData(option, growth.data_source, growth.growthtype)
        elif data_analysis == "CustomerGrowth":
            growth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
            X_test = self._getHistoricalData(option, growth.data_source, growth.growthtype)
        elif data_analysis == "CumulativeOrdersGrowth":
            growth = GrowthModel("CumulativeOrdersGrowth", "cumulative_growth", data_source=OrdersAmount())
            X_test = self._getHistoricalData(option, growth.data_source, growth.growthtype)
        elif data_analysis == "OrdersGrowth":
            growth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())
            X_test = self._getHistoricalData(option, growth.data_source, growth.growthtype)
        
        try:

            pred = growth.predict(X_test, self.model, self.scaler_y, self.scaler_X, OPTIONS[option]["lag"], OPTIONS[option]["rolling_mean"], OPTIONS[option]["sequence_lenght"], option)
        
        except Exception as e:
            raise Exception(f"Failed to predict: {e}")

        return pred
    
    def _getHistoricalData(self, option:str, data_source: CustomerSignup | OrdersAmount, growthtype: str):
        amount_historical_data = 0
        if growthtype == "cumulative_growth":
            index = 1
        elif growthtype == "growth":
            index = 0
        try:
            if option == "one_day":
                amount_historical_data = 2 * OPTIONS[option]["sequence_lenght"] + max(OPTIONS[option]["rolling_mean"], OPTIONS[option]["lag"]) + OPTIONS[option]["rolling_mean"]
                X_data = data_source.perform(last_days=amount_historical_data, showzeros=True)
                analysis = list(X_data.keys())[index]
                X_data = X_data[analysis]
                X_data = self._prepare_test_data(X_data, OPTIONS[option]["lag"], OPTIONS[option]["rolling_mean"], amount_historical_data=amount_historical_data, growthtype=growthtype)
            elif option == "seven_days":
                amount_historical_data = 2 * OPTIONS[option]["sequence_lenght"] + max(OPTIONS[option]["rolling_mean"], OPTIONS[option]["lag"]) + OPTIONS[option]["rolling_mean"]
                X_data = data_source.perform(last_days=amount_historical_data, showzeros=True)
                analysis = list(X_data.keys())[0]
                X_data = X_data[analysis]
                X_data = self._prepare_test_data(X_data, OPTIONS[option]["lag"], OPTIONS[option]["rolling_mean"], amount_historical_data=amount_historical_data, growthtype=growthtype)
            elif option == "month":
                amount_historical_data = OPTIONS[option]["sequence_lenght"] + OPTIONS[option]["rolling_mean"]
                X_data = data_source.perform(month=True, showzeros=True)
                print(X_data)
                analysis = list(X_data.keys())[index]
                X_data = X_data[analysis]
                X_data = self._prepare_test_data(X_data, OPTIONS[option]["lag"], OPTIONS[option]["rolling_mean"], amount_historical_data=amount_historical_data, growthtype=growthtype)
            elif option == "year":
                amount_historical_data = OPTIONS[option]["sequence_lenght"] + OPTIONS[option]["rolling_mean"]
                X_data = data_source.perform(year=True, showzeros=True)
                analysis = list(X_data.keys())[index]
                X_data = X_data[analysis]
                X_data = self._prepare_test_data(X_data, OPTIONS[option]["lag"], OPTIONS[option]["rolling_mean"], amount_historical_data=amount_historical_data, growthtype=growthtype)
            return X_data
        except Exception as e:
            raise Exception(f"Failed to get historical data: {e}")
        
    def _prepare_test_data(self, X_test_raw, lag, rolling_mean, amount_historical_data: int, growthtype:str):
        try:
            print(X_test_raw)
            X = np.array([self._to_datetime_timestamp(key) for key in X_test_raw])
            y = np.array([int(X_test_raw[value]) for value in X_test_raw])
            df = pd.DataFrame(y, columns=[growthtype])
            df['timestamp'] = X

            df.drop(columns=[growthtype], inplace=True)

            for i in range(1, lag + 1):
                df[f'lag_{i}'] = df['timestamp'].shift(i)

            df['rolling_mean'] = df['timestamp'].rolling(window=rolling_mean).mean()
            df.dropna(inplace=True)

        except Exception as e:
            raise e

        return df

        