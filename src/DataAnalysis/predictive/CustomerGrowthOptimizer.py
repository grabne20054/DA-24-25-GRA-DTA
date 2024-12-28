
from predictive.CustomerGrowth import CustomerGrowth
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.optimizers import Adam
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime
import threading
import time


mlflow.set_tracking_uri("http://192.168.33.24:5000")
mlflow.set_experiment('CustomerGrowth')
print('Successfully connected to MLFlow server')

class CustomerGrowthOptimizer:
    def __init__(self) -> None:
        self.customer_growth = CustomerGrowth()

    def collect(self):
        return self.customer_growth.provide_data_to_perform()
    
    def spawn_thread(self, n:int=5):
        for i in range(n):
            thread = threading.Thread(target=self.get_best_params)
            thread.start()
    

    def get_best_params(self):
        X_train, X_test, y_train, y_test, scaler_X, scaler_y = self.collect()

        results = {}
        for num_units in [50, 100, 200, 300, 400, 500]:
            for dropout in [0.1, 0.2, 0.3]:
                for learning_rate in [0.1, 0.01, 0.001]:
                    for epoch in [1000, 2000, 3000]:

                        print('Running with', num_units, 
                            'LSTM cells, dropout =', dropout, 
                            'and learning rate =', learning_rate, '...')
                        
                        model = Sequential([
                            LSTM(num_units, input_shape=(X_train.shape[1], X_train.shape[2])),
                            Dense(1)
                        ])
                        optimizer = Adam(learning_rate=learning_rate)
                        model.compile(optimizer=optimizer, loss='mse')

                        history = model.fit(X_train, y_train, epochs=epoch, batch_size=64, validation_data=(X_test, y_test), verbose=1)

            
                        num_epochs = len(history.history['val_loss'])
                        best_epoch = np.argmin(history.history['val_loss'])
                        train_mse = history.history['loss'][best_epoch]
                        val_mse = history.history['val_loss'][best_epoch] 
                        results[(num_units, dropout, learning_rate, best_epoch)] = {'train_mse': train_mse, 
                                                                                'val_mse': val_mse}                                                                                          
                        print('Train MSE =', train_mse, ', Validation MSE =', val_mse)        
                        print('+----------------------------------------------------------------------+')

        val_results = {key: results[key]['val_mse'] for key in results.keys()}
        num_cells, dropout_rate, lr, num_epochs = min(val_results, key=val_results.get)
        print('Best parameters:', num_cells, 
                'LSTM cells, training for', num_epochs, 
                'epochs with dropout =', dropout_rate, 
                'and learning rate =', lr)
        
        self.save_best_params('CustomerGrowth' + str(datetime.now()), num_cells, dropout_rate, lr, num_epochs, results[(num_cells, dropout_rate, lr, num_epochs)]['train_mse'], results[(num_cells, dropout_rate, lr, num_epochs)]['val_mse'])
        



        return num_epochs, best_epoch, learning_rate, dropout_rate
    
    def save_best_params(self, run_name, num_units, dropout, learning_rate, epoch, train_mse, val_mse):
        mlflow.start_run(run_name=run_name)
        mlflow.log_param('num_units', num_units)
        mlflow.log_param('dropout', dropout)
        mlflow.log_param('learning_rate', learning_rate)
        mlflow.log_param('epoch', epoch)
        mlflow.log_metric('train_mse', train_mse)
        mlflow.log_metric('val_mse', val_mse)

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
            order_by=["metrics.accuracy DESC"]
        )[0]
            
        best_run_params = best_run.data.params

        self.customer_growth.perform(best_run_params['num_units'], best_run_params['dropout'], best_run_params['learning_rate'], best_run_params['epoch'])

if __name__ == '__main__':
    cgo = CustomerGrowthOptimizer()
    cgo.spawn_thread()