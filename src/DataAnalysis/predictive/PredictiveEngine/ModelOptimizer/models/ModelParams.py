from pydantic import BaseModel
import tensorflow as tf
from sklearn.pipeline import Pipeline

class ModelParams(BaseModel, arbitrary_types_allowed=True):
    run_name: str
    num_units: int
    dropout: float
    learning_rate: float
    epoch: int
    l2_reg: float
    train_mse: float
    val_mse: float
    train_mae: float
    val_mae: float
    model: tf.keras.Sequential
    input_example: list
    scaler_y: Pipeline
    scaler_X: Pipeline
    lag: int
    rolling_mean: int
    sequence_length: int