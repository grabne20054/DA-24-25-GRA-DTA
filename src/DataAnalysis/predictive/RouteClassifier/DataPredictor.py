import os
import pickle
import mlflow
import mlflow.artifacts
from mlflow.sklearn import load_model
from mlflow.tracking import MlflowClient

from DataAnalysis.db.models.RouteClassifier import RouteClassifierRepository
from DataAnalysis.db.models.queryparams import RouteClassifierParam as RouteClassifierParams
from DataAnalysis.DataCollector import DataCollector

import numpy as np
import pandas as pd
from os import getenv
os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = "5"
os.environ["MLFLOW_HTTP_REQUEST_MAX_RETRIES"] = "1"


class DataPredictor(DataCollector):

    def __init__(self, data_analysis: str):
        super().__init__()
        self.model = None
        self.scaler_X = None
        self.data_analysis = data_analysis

    # -------------------------------
    # Data collection
    # -------------------------------
    def collect(self) -> list[RouteClassifierParams]:
        """
        Collects data from the DB

        Returns:
            list: List of dictionaries containing the data
        """
        try:
            return RouteClassifierRepository(self.db).get()
        except ConnectionRefusedError as e:
            print("Connection refused: ", e)
        except ConnectionError as e:
            print("Connection error: ", e)
        except Exception as e:
            print("Error: ", e)

    # ---------------------------------------------------------
    # LOAD BEST MODEL FROM MLFLOW
    # ---------------------------------------------------------
    def _get_best_model_id(self):
        try:
            client = MlflowClient(tracking_uri=getenv("MLFLOWURL"))
            mlflow.set_tracking_uri(getenv("MLFLOWURL"))
            experiment = client.get_experiment_by_name("ClassifierEx")
            if experiment is None:
                raise Exception("Experiment not found")
        except Exception:
            raise Exception(f"Error connecting to MLflow")
        
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=f"attributes.run_name = '{self.data_analysis}'",
            run_view_type=mlflow.entities.ViewType.ACTIVE_ONLY,
            max_results=1,
            order_by=["params.overall_score ASC"]
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
        if self.scaler_X is None:
            raise Exception("ScalerX is None")

    # ---------------------------------------------------------
    # PREDICT
    # ---------------------------------------------------------
    def predict(self, coords: tuple[float, float]):

        if self.model is None:
            self.load_best_model()

        coords = np.array(coords).reshape(1, -1)

        coords_scaled = self.scaler_X.transform(coords)

        y_pred = self.model.predict(coords_scaled)

        routeId = self._mapDiscreteNumberToRouteId(discrete_number=y_pred.tolist()[0], data=self.collect())

        return {"predicted_routeId": routeId}
    

    def _mapDiscreteNumberToRouteId(self, discrete_number: int, data: list[RouteClassifierParams]) -> str:
        classes = [item.routeId for item in data if item.latitude is not None and item.longitude is not None]

        unique_routes = sorted(set(classes))
        route_to_number = {route: i for i, route in enumerate(unique_routes)}
        number_to_route = {i: route for route, i in route_to_number.items()}
        return number_to_route.get(discrete_number, None)