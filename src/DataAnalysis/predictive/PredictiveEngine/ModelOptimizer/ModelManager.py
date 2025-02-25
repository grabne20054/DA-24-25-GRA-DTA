import mlflow
from mlflow.tracking import MlflowClient
from os import getenv
from dotenv import load_dotenv
load_dotenv()

OPTIONS = {"one_day": {"lag": 2, "sequence_lenght": 5, "rolling_mean": 3}, "seven_days": {"lag": 3, "sequence_lenght": 7, "rolling_mean": 7}, "month": {"lag": 2, "sequence_lenght": 2, "rolling_mean": 3}, "year": {"lag": 1, "sequence_lenght": 1, "rolling_mean": 2}}

class ModelManager:
    def __init__(self):
        self._setup_mlflow()


    def _setup_mlflow(self):
        mlflow.set_tracking_uri(getenv('MLFLOWURL'))
        if mlflow.set_experiment("GrowthEx") is None:
            mlflow.create_experiment("GrowthEx")
        print('Successfully connected to MLFlow server')

    def getModels(self, config: list):
        try:
            client = MlflowClient(tracking_uri=getenv("MLFLOWURL"))
            mlflow.set_tracking_uri(getenv("MLFLOWURL"))
            experiment = client.get_experiment_by_name("GrowthEx")
            print("run lenght", len(client.search_runs(experiment_ids=[experiment.experiment_id])), len(config))


            if experiment is None:
                raise Exception('Experiment not found')
            else: 
                for i in range(len(config)):
                    data_analysis, growthtype, option = config[i]
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
                        order_by=["metrics.train_mse ASC", "metrics.train_mae ASC", "start_time ASC"]
                    )

                    if not runs:
                        print('No runs found for the given parameters')
                        continue

                    best_run = runs[0]
                    self.deleteModel(best_run.info.run_id)
        except Exception as e:
            raise e
        
    def deleteModel(self, run_id: str):
        try:
            client = MlflowClient(tracking_uri=getenv("MLFLOWURL"))
            mlflow.set_tracking_uri(getenv("MLFLOWURL"))
            client.delete_run(run_id)
        except Exception as e:
            raise e