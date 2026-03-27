import os
import sys
import logging
from os import getenv
import pickle

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import mlflow
from mlflow.sklearn import log_model

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from DataAnalysis.db.models.RouteClassifier import RouteClassifierRepository
from DataAnalysis.db.models.queryparams import RouteClassifierParam as RouteClassifierParams
from DataAnalysis.DataCollector import DataCollector

from DataAnalysis.predictive.ModelOptimizer.models.ModelData import ClassificationModelData
from DataAnalysis.predictive.ModelOptimizer.models.ModelParams import ClassificationModelParams

from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score

# -------------------------------
# Logger setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("classifier_model.log")
    ]
)
logger = logging.getLogger(__name__)

# -------------------------------
# Global constants
# -------------------------------
MODEL_DIR = '/models/'
TYPEOFGRAPH = "line"

load_dotenv()

# -------------------------------
# ClassifierModel class
# -------------------------------
class ClassifierModel(DataCollector):
    def __init__(self) -> None:
        super().__init__()
        self.setup_mlflow()
        self.experiment = 'ClassifierEx'

    # -------------------------------
    # MLFlow setup
    # -------------------------------
    def setup_mlflow(self):
        try:
            mlflow.set_tracking_uri(getenv('MLFLOWURL'))
            logger.info("Successfully connected to MLFlow server")
        except Exception:
            logger.exception("Error connecting to MLFlow server")

    def get_experiment_id(self, experiment_name: str) -> str:
        try:
            client = mlflow.tracking.MlflowClient(tracking_uri=getenv("MLFLOWURL"))
            mlflow.set_tracking_uri(getenv("MLFLOWURL"))
            experiment = client.get_experiment_by_name(experiment_name)
            if experiment is None:
                raise Exception(f"Experiment '{experiment_name}' not found")
            return experiment.experiment_id
        except Exception as e:
            logger.exception(f"Error retrieving experiment ID for '{experiment_name}'")
            raise Exception(f"Error retrieving experiment ID for '{experiment_name}'") from e

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

    # -------------------------------
    # Normalization
    # -------------------------------
    def _normalize(self, train, test):
        if len(train) == 0 or len(test) == 0:
            raise ValueError("Training or testing data is empty.")
        
        if type(train) != np.ndarray or type(test) != np.ndarray:
            train = np.array(train)
            test = np.array(test)

        if train.ndim == 1 or test.ndim == 1:
            train = train.reshape(-1, 1)
            test = test.reshape(-1, 1)
        
        logger.info(f"Train shape before normalization: {train.shape}")
        logger.info(f"Test shape before normalization: {test.shape}")
        pipeline = StandardScaler()
        train = pipeline.fit_transform(train)
        test = pipeline.transform(test)

        return train, test, pipeline


    # -------------------------------
    # Training and hyperparameter search
    # -------------------------------
    def find_best_params(self):

        data = self.collect()
        
        if data is None:
            logger.error("No data collected")
            raise ValueError("No data collected")
        if len(data) == 0:
            logger.error("No data collected")
            raise ValueError("No data collected")
        
        self.neighbors = len(sorted(set([item.routeId for item in data if item.latitude is not None and item.longitude is not None])))


        self.classes = self._mapRouteIdToDiscreteNumber(data)
        latitude_list = [item.latitude for item in data if item.latitude is not None and item.longitude is not None]
        longitude_list = [item.longitude for item in data if item.latitude is not None and item.longitude is not None]

        coordinates = np.column_stack((latitude_list, longitude_list))

        try:
            X_train, X_test, y_train, y_test = train_test_split(coordinates, self.classes, test_size=0.1, random_state=0, shuffle=True)
        except Exception as e:
            logger.exception("Error splitting data into train and test sets")
            raise Exception("Error splitting data into train and test sets")

        try:
            X_train, X_test, scaler_X = self._normalize(X_train, X_test)
        except Exception as e:
            logger.exception("Error normalizing data")
            raise Exception("Error normalizing data")

        modeldata = ClassificationModelData(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            scaler_X=scaler_X,
        )

        params = self.run(modeldata)
        self.save_best_model(params)

        return None

    def run(self, modeldata: ClassificationModelData) -> ClassificationModelParams:

        with mlflow.start_run(experiment_id=self.get_experiment_id(self.experiment)):

            results = {}
            for neighbor in range(1, self.neighbors):
                logger.info(f"Training KNN with n_neighbors={neighbor}")

                try:
                    model = KNeighborsClassifier(n_neighbors=neighbor)
                    model.fit(modeldata.X_train, modeldata.y_train)
                    y_pred = model.predict(modeldata.X_test)

                except Exception as e:
                    logger.exception(f"Error training KNN with n_neighbors={neighbor}")
                    raise Exception(f"Error training KNN with n_neighbors={neighbor}")


                accuracy = accuracy_score(y_true=modeldata.y_test, y_pred=y_pred)
                precision = precision_score(y_true=modeldata.y_test, y_pred=y_pred, average='weighted', zero_division=np.nan)
                recall = recall_score(y_true=modeldata.y_test, y_pred=y_pred, average='weighted', zero_division=np.nan)

                overall_score = 2*(1+accuracy)+ precision + recall

                results[(neighbor, model)] = {
                    "overall_score": overall_score,
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                }

            best_params = max(results, key=lambda x: results[x]['overall_score'])

            return ClassificationModelParams(
                run_name="RouteClassifier",
                overall_score=results[best_params]['overall_score'],
                accuracy=results[best_params]['accuracy'],
                precision=results[best_params]['precision'],
                recall=results[best_params]['recall'],
                model=best_params[1],
                input_example=modeldata.X_train[0],
                scaler_X=modeldata.scaler_X

            )


    # -------------------------------
    # Save model and scalers
    # -------------------------------
    def save_best_model(self, params: ClassificationModelParams):
        try:
            mlflow.log_param('run_name', params.run_name)
            mlflow.log_param('overall_score', params.overall_score)
            mlflow.log_param('accuracy', params.accuracy)
            mlflow.log_param('precision', params.precision)
            mlflow.log_param('recall', params.recall)

            log_model(params.model, 'model') # TODO input example and signature
            self._save_scaler(params.scaler_X, "scaler_X.pkl")

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

    def perform(self):
        self.find_best_params()
    
    def _mapRouteIdToDiscreteNumber(self, data: list[RouteClassifierParams]):
        classes = [item.routeId for item in data if item.latitude is not None]

        unique_routes = sorted(set(classes))
        route_to_number = {route: i for i, route in enumerate(unique_routes)}

        classes_mapped = [route_to_number[route] for route in classes]

        return classes_mapped
