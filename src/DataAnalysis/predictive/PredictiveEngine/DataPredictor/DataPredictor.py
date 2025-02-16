import mlflow.artifacts
from mlflow.tensorflow import load_model
from mlflow.tracking import MlflowClient
from datetime import datetime
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
        self.scaler = None
        self.data_analysis = data_analysis

    def _get_best_model_id(self, data_analysis:str, option:str) -> str:
        try:
            client = MlflowClient(tracking_uri=getenv("MLFLOWURL"))
            mlflow.set_tracking_uri(getenv("MLFLOWURL"))
            experiment = client.get_experiment_by_name("GrowthEx")

            print(data_analysis)

            print(OPTIONS[option]['lag'], OPTIONS[option]['sequence_lenght'], OPTIONS[option]['rolling_mean'])

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
                
            print(runs)

            if not runs:
                raise Exception('No runs found for the given parameters')

            best_run = runs[0]

            print(best_run.info.run_id, best_run.info.artifact_uri)
                
            return best_run.info.run_id, best_run.info.artifact_uri
        except Exception as e:
            raise e

    def _getScalerOfModel(self, run_id: str):
        try:
            scaler_local = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="model/scaler.pkl")

            if not os.path.exists(scaler_local):
                raise FileNotFoundError(f"Scaler file not found at {scaler_local}")

            artifacts = mlflow.artifacts.list_artifacts(run_id=run_id, artifact_path="model")

            with open(scaler_local, "rb") as f:
                scaler = pickle.load(f)

            self.scaler = scaler

        except Exception as e:
            raise Exception(f"Failed to retrieve scaler: {e}")

            

    def loadBestModel(self, data_analysis:str, option:str):
        best_model_id, artifact_uri = self._get_best_model_id(data_analysis, option)
        model_url = f"{artifact_uri}/model"
        self.model = load_model(model_url)
        self._getScalerOfModel(best_model_id)

    def _to_datetime_timestamp(self, date: datetime):
        return date.timestamp()
        

    def predict(self, X_pred, data_analysis:str, option:str):
        self.loadBestModel(data_analysis, option)
        if self.model is None:
            raise Exception("Model not loaded")
        if self.scaler is None:
            raise Exception("Scaler not loaded")

        if data_analysis == "CumulativeCustomerGrowth":
            growth = GrowthModel("CumulativeCustomerGrowth", "cumulative_growth", data_source=CustomerSignup())
            X_test = self._getTestData(option, growth.data_source)
            X_test = X_test['cumulative_growth']
        elif data_analysis == "CustomerGrowth":
            growth = GrowthModel("CustomerGrowth", "growth", data_source=CustomerSignup())
            X_test = self._getTestData(option, growth.data_source)
            X_test = X_test['growth']
        elif data_analysis == "CumulativeOrdersGrowth":
            growth = GrowthModel("CumulativeOrdersGrowth", "cumulative_growth", data_source=OrdersAmount())
            X_test = self._getTestData(option, growth.data_source)
            X_test = X_test['cumulative_growth']
        elif data_analysis == "OrdersGrowth":
            growth = GrowthModel("OrdersGrowth", "growth", data_source=OrdersAmount())
            X_test = self._getTestData(option, growth.data_source)
            X_test = X_test['growth']
        
        try:

            pred = growth.predict(X_test, X_pred ,self.model, self.scaler, OPTIONS[option]["lag"], OPTIONS[option]["rolling_mean"], OPTIONS[option]["sequence_lenght"])
        
        except Exception as e:
            raise Exception(f"Failed to predict: {e}")

        return pred
    
    def _getTestData(self, option:str, data_source: CustomerSignup | OrdersAmount):
        amount_historical_data = 0
        if option == "one_day":
            amount_historical_data = 2 * OPTIONS[option]["sequence_lenght"] + max(OPTIONS[option]["rolling_mean"], OPTIONS[option]["lag"]) + 3
            X_data = data_source.perform(last_days=amount_historical_data)
        elif option == "seven_days":
            amount_historical_data = 2 * OPTIONS[option]["sequence_lenght"] + max(OPTIONS[option]["rolling_mean"], OPTIONS[option]["lag"]) + 3
            X_data = data_source.perform(last_days=amount_historical_data)
        elif option == "month":
            amount_historical_data = 2 * OPTIONS[option]["sequence_lenght"] + max(OPTIONS[option]["rolling_mean"], OPTIONS[option]["lag"]) + 3
            X_data = data_source.perform(last_days=amount_historical_data)
        elif option == "year":
            amount_historical_data = 2 * OPTIONS[option]["sequence_lenght"] + max(OPTIONS[option]["rolling_mean"], OPTIONS[option]["lag"]) + 3
            X_data = data_source.perform(last_days=amount_historical_data)
        
        return X_data
        