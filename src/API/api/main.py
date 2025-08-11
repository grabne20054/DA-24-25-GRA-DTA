from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import descriptive, diagnostic, predictive, auth



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(descriptive.router)
app.include_router(diagnostic.router)
app.include_router(predictive.router)
app.include_router(auth.router)
