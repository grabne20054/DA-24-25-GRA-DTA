from DataAnalysis.APIDataHandler import APIDataHandler

class APIDataHandlerFactory:
    """ Factory for creating APIDataHandler objects"""
    @staticmethod
    def create_data_handler(url: str) -> APIDataHandler:
        """
        Creates a new APIDataHandler object

        Args:
            url (str): URL to the API

        Returns:
            APIDataHandler: APIDataHandler object
        """
        return APIDataHandler(url)