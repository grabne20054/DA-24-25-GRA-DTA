from DataAnalysis.APIDataHandler import APIDataHandler

class APIDataHandlerFactory:
    @staticmethod
    def create_data_handler(url: str) -> APIDataHandler:
        return APIDataHandler(url)