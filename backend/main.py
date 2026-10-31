from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Decathlon Nutrition API")

class Mesure(BaseModel):
    scale_id: str
    weight_kg: float

mesures = []  # stockage temporaire en mémoire, remplacé plus tard par une base

@app.get("/")
def accueil():
    return {"message": "API nutrition Decathlon en ligne"}

@app.post("/mesures")
def recevoir_mesure(m: Mesure):
    entree = {**m.model_dump(), "timestamp": datetime.now().isoformat()}
    mesures.append(entree)
    return entree

@app.get("/mesures")
def lister_mesures():
    return mesures