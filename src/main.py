from DataAnalysis.APIDataHandler import APIDataHandler

handler = APIDataHandler("http://localhost:8002/addresses")
data = handler.start()
print(data)