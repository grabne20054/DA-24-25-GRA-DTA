import requests, json
from DataAnalysis.REMOVINGS import REMOVINGS



class APIDataHandler:
    def __init__(self, url):
        self.url = url

    def fetch(self):
        print("fetch")
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception("API response: {}".format(response.status_code))
        return response.json()
    
    def removeMissingorNullValues(self):
        '''with open('DataAnalysis/test.json', 'r') as f: # MOCK
            data = json.load(f)'''
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

    def handleCaseSensitivity(self):
        '''with open('DataAnalysis/test.json', 'r') as f: # MOCK
            data = json.load(f)'''
        data = self.removeMissingorNullValues()

        for i in data:
            for key in list(i.keys()):
                    if isinstance(i[key], str):
                        i[key] = str(i[key]).lower()

        return data
    
    def removeDuplicates(self):
        '''with open('DataAnalysis/test.json', 'r') as f: # MOCK
            data = json.load(f)'''
        
        data = self.handleCaseSensitivity()

        seen = set()
        clean = []
        
        for i in data:
            dict_tuple = frozenset(i.items()) # Convert dict to hashable form
            if dict_tuple not in seen:
                seen.add(dict_tuple)
                clean.append(i)

        return clean
    
    def removeAllWhitespaces(self):
        '''with open('DataAnalysis/test.json', 'r') as f:
            data = json.load(f)'''
        
        data = self.removeDuplicates()

        for i in data:
            for key in list(i.keys()):
                if isinstance(i[key], str):
                    i[key] = str(i[key]).replace(" ", "")
        return data

    def start(self):
        return self.removeAllWhitespaces()          
                        

                    
        
            

           