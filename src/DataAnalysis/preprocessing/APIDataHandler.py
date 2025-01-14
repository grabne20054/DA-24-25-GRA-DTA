import requests, json
from DataAnalysis.preprocessing.REMOVINGS import REMOVINGS



class APIDataHandler:
    """
    Class to handle API data
    """
    def __init__(self, url):
        self.url = url

    def fetch(self) -> list:
        """
        Fetches data from the API
        
        Returns:
            list: List of dictionaries containing the data
        """
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception("API response: {}".format(response.status_code))
        return response.json()
    
    def removeMissingorNullValues(self) -> list:
        """
        Removes missing or null values

        Returns:
            list: List of dictionaries containing the clean data
        """
        data = self.fetch()

        clean = []

        for i in data:
            removeable_record = False
            for key in list(i.keys()):
                if key in [i.value for i in REMOVINGS]:
                    if i[key] == None or i[key] == "":
                        removeable_record = True
                        break
                else:
                    if i[key] == None or i[key] == "":
                        i.pop(key)
                if key == None or key == "":
                    i.pop(key)
            if not removeable_record:
                clean.append(i)
        return clean

    def handleCaseSensitivity(self) -> list:
        """
        Handles case sensitivity
        
        Returns:
            
            list: List of dictionaries containing the clean data
        """
        data = self.removeMissingorNullValues()

        for i in data:
            for key in list(i.keys()):
                    if isinstance(i[key], str):
                        i[key] = str(i[key]).lower()

        return data
    
    def removeDuplicates(self) -> list:
        """
        Removes duplicates

        Returns:
            list: List of dictionaries containing the clean data
        """
        data = self.handleCaseSensitivity()

        seen = set()
        clean = []
        
        for i in data:
            dict_tuple = frozenset(i.items()) # Convert dict to hashable form
            if dict_tuple not in seen:
                seen.add(dict_tuple)
                clean.append(i)

        return clean
    
    def removeAllWhitespaces(self) -> list:
        """
        Removes all whitespaces
        
        Returns:
            list: List of dictionaries containing the clean data
        """
        data = self.removeDuplicates()

        for i in data:
            for key in list(i.keys()):
                if isinstance(i[key], str):
                    i[key] = str(i[key]).replace(" ", "")
        return data

    def start(self) -> list:
        """
        Starts the data handling process

        Returns:
            list: List of dictionaries containing the clean data, invokes whole preprocessing pipeline
        """
        return self.removeAllWhitespaces()          
                        

                    
        
            

           