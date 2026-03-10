from DataAnalysis.preprocessing.APIDataHandler import APIDataHandler

DeprecationWarning("APIDataHandlerFactory is deprecated. APIDataHandlerFactory will be removed in future versions.")

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