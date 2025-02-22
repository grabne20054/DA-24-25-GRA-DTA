# DA-24-25-GRA-DTA

## HOW TO RUN

### Benötigte Ressourcen

### ENV File

unter DA-24-25-GRA-DTA\src\DataAnalysis\.env

APIURL="http://host.docker.internal:8002"
MLFLOWURL="http://host.docker.internal:5000"
JWT_SECRET_KEY=0417a12ff4619c7f9110d3f724f388e799a75ec08f5065e45c6d5822711f516af8a05b14f4a894ac66e8faf75e63e7057e8eb2a9c7c2c556efd6a14b36c5c1a21d25a267ee3861e456f7a630a32c75d7b6d8c89ff0f1cd82391e7f1a455d59ed8e1f6da45fb343c6bbb0dc809b85d55599ce35799c773b52727afe4b72d33bf6dcd6f68b401a098b0acb7771f0763e3598bacdf1af09995d0bdf1d12f2706dfbee70de8c4bb80891e4ff026343c09233aa2da50a7cdc669e59dbb4ca126c2693d3bf0c2725909fc6888a66c501d24274a7ebd667b121efdd955e94c2db4880c1d024f8cf3bfec9d2d353bd018e7b590c271d144f3b09828c4078189427042509a5d10ee4cbb4c13f0fd211861843975d882d59d27e167ecaa6c385108db5df865f14f8106c8964428de4046f83770033b853153f7ab3714d177424a30b181255973ce94d69ab0f1ccb10250943ba2507580d47c48bc61fe19964146dd691ba09288dd5ab42d04170779a71b751c6262200769f795d9af78d5bf9d610364d4f57d2001a04c742d31a3ac84b448ec3f5ddfd2ecae77569d870d7969d40c510ff0b273621c6d42f44e15d2e51a4e9e20785e0733cb7dd25b859049a4bae7a53602f285f2573a8dbf915a1dd528ebb84a62c2784c43092220890917bc2ff5c5c80a67c8944e93e88efc3b35d89ff531d8386b31625c656ba265ac43294b18e2bbef2

### API für DB Calls

1. MOCK Daten API

- git clone https://github.com/htlweiz/DA-24-25-DB-API-DTA

- docker compose up --build -d

- DA-24-25-GRA-DTA\mock_data.py ausführen, um Datenbank zu befüllen

oder

2. Test DB AP benutzen, welche bereits mit Mock Daten befüllt wurde

- APIURL im .env wie folgt ändern:

* APIURL="http://185.243.187.210:8002"

### API für Datenanalysen

unter DA-24-25-GRA-DTA\src\API

- docker compose up --build -d ausführen

für jede Datenanalyse (ausser ItemsBoughtCorrelation) ist ein Token notwendig!
unter /api/authenticate (am besten bei docs schauen) kann mit admin credentials ein solcher generiert werden:

email: admin
password: admin

dieser muss dann als query parameter mitangegeben werden!

für predictive vorhersagen ist der untere schritt notwendig:

### ModelOptimizer + MLFLOW (Models erstellen und speichern)

unter DA-24-25-GRA-DTA\src\DataAnalysis\predictive\PredictiveEngine

- docker compose up --build

ausführen
