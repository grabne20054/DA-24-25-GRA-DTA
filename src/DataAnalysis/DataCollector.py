from DataAnalysis.dependencies import get_db

class DataCollector:
    def __init__(self) -> None:
        self.db = next(get_db())
