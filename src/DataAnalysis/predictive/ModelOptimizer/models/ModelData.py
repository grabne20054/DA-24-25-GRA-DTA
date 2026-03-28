from pydantic import BaseModel
from numpy import ndarray
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

class ModelData(BaseModel, arbitrary_types_allowed=True):
    X_train: ndarray
    y_train: ndarray
    X_test: ndarray
    y_test: ndarray
    scaler_X: Pipeline
    scaler_y: Pipeline
    lag: int
    rolling_mean: int
    sequence_length: int

class ClassificationModelData(BaseModel, arbitrary_types_allowed=True):
    X_train: list
    y_train: list
    X_test: list
    y_test: list
    scaler_X: StandardScaler
