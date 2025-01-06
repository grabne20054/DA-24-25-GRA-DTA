from DataAnalysis.predictive.CustomerGrowth import CustomerGrowth
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM, Bidirectional
from tensorflow.keras.optimizers import Adam
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime
import threading
import time
from math import isnan


class CustomerGrowthOptimizer:
    def __init__(self) -> None:
        self.customer_growth = CustomerGrowth()
        self.setup_mlflow()

    def setup_mlflow(self):
        mlflow.set_tracking_uri("http://192.168.33.24:5000")
        mlflow.set_experiment('CustomerGrowth')
        print('Successfully connected to MLFlow server')


    def collect(self):
        return self.customer_growth.provide_data_to_perform()
    
    def spawn_thread(self, n:int=5):
        for i in range(n):
            thread = threading.Thread(target=self.get_best_params)
            thread.start()
    

    def get_best_params(self):
        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self.collect()

        results = {}
        for num_units in [16, 32, 64, 128]:
            for dropout in [0.1, 0.2, 0.3]:
                for learning_rate in [1e-5, 1e-4, 1e-3, 1e-2]:
                    for epoch in [50, 100, 150, 200]:

                        print('Running with', num_units, 
                            'LSTM cells, dropout =', dropout, 
                            'and learning rate =', learning_rate, '...')
                        
                        model = Sequential([
                            Bidirectional(LSTM(num_units, input_shape=(X_train.shape[1], X_train.shape[2]), kernel_regularizer=tf.keras.regularizers.l2(0.01), dropout=dropout, return_sequences=True)),
                            Bidirectional(LSTM(num_units, dropout=dropout, return_sequences=True)),
                            Bidirectional(LSTM(num_units, dropout=dropout)),
                            Dense(1)
                        ])
                        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=['mse', 'mae', 'accuracy'])

                        history = model.fit(X_train, y_train, epochs=epoch, batch_size=32,  validation_data=(X_test, y_test), verbose=1)

            
                        num_epochs = len(history.history['val_loss'])
                        best_epoch = np.argmin(history.history['val_loss'])

                        train_mse = history.history['loss'][best_epoch]
                        val_mse = history.history['val_loss'][best_epoch] 
                        train_mae = history.history['mae'][best_epoch]
                        val_mae = history.history['val_mae'][best_epoch]
                        train_accuracy = history.history['accuracy'][best_epoch]
                        val_accuracy = history.history['val_accuracy'][best_epoch]

                        results[(num_units, dropout, learning_rate, best_epoch)] = {'train_mse': train_mse, 
                                                                                'val_mse': val_mse}                                                                                          
                        print('Train MSE =', train_mse, ', Validation MSE =', val_mse, ', Train MAE =', train_mae, ', Validation MAE =', val_mae, ', Train Accuracy =', train_accuracy, ', Validation Accuracy =', val_accuracy)        
                        print('+----------------------------------------------------------------------+')

        val_results = {key: results[key]['val_mse'] for key in results.keys()}
        num_cells, dropout_rate, lr, num_epochs = min(val_results, key=val_results.get)
        print('Best parameters:', num_cells, 
                'LSTM cells, training for', num_epochs, 
                'epochs with dropout =', dropout_rate, 
                'and learning rate =', lr)
        
        if not isnan(results[(num_cells, dropout_rate, lr, num_epochs)]['val_mse']):
        
            self.save_best_params('CustomerGrowth' + str(datetime.now()), num_cells, dropout_rate, lr, num_epochs, results[(num_cells, dropout_rate, lr, num_epochs)]['train_mse'], results[(num_cells, dropout_rate, lr, num_epochs)]['val_mse'], results[(num_cells, dropout_rate, lr, num_epochs)]['train_mae'], results[(num_cells, dropout_rate, lr, num_epochs)]['val_mae'],results[(num_cells, dropout_rate, lr, num_epochs)]['train_accuracy'], results[(num_cells, dropout_rate, lr, num_epochs)]['val_accuracy'])
        else:
            print('Invalid results. Skipping...')
        



        return num_epochs, best_epoch, learning_rate, dropout_rate
    
    def save_best_params(self, run_name, num_units, dropout, learning_rate, epoch, train_mse, val_mse, train_mae, val_mae, train_accuracy, val_accuracy):
        mlflow.start_run(run_name=run_name)
        mlflow.log_param('num_units', num_units)
        mlflow.log_param('dropout', dropout)
        mlflow.log_param('learning_rate', learning_rate)
        mlflow.log_param('epoch', epoch)


        mlflow.log_metric('train_mse', train_mse)
        mlflow.log_metric('val_mse', val_mse)
        mlflow.log_metric('train_mae', train_mae)
        mlflow.log_metric('val_mae', val_mae)
        mlflow.log_metric('train_accuracy', train_accuracy)
        mlflow.log_metric('val_accuracy', val_accuracy)

        print('Run', run_name, 'saved successfully')
        print('+----------------------------------------------------------------------+')

        
        self.get_best_model()

    def get_best_model(self):
        client = MlflowClient()
        experiment = client.get_experiment_by_name('CustomerGrowth')

        if experiment is None:
            raise Exception('Experiment not found')
        else: 
            best_run = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="",
            run_view_type=mlflow.entities.ViewType.ACTIVE_ONLY,
            max_results=1,
            order_by=["metrics.train_accuracy DESC", "metrics.train_mse DESC", "metrics.train_mae DESC"]
        )[0]
            
        best_run_params = best_run.data.params
            
        num_units = int(best_run_params['num_units'])
        dropout = float(best_run_params['dropout'])
        learning_rate = float(best_run_params['learning_rate'])
        epoch = int(best_run_params['epoch'])

        self.customer_growth.perform(num_units, dropout, learning_rate, epoch)

if __name__ == '__main__':
    cgo = CustomerGrowthOptimizer()
    cgo.spawn_thread()