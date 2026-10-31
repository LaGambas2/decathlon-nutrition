from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import creer_tables, get_session
from backend.models import Client, ClientIn, Mesure, MesureIn

creer_tables()

app = FastAPI(title="Decathlon Nutrition API")


@app.get("/")
def accueil():
    return {"message": "API nutrition Decathlon en ligne"}


@app.post("/clients")
def creer_client(c: ClientIn, session: Session = Depends(get_session)):
    client = Client(**c.model_dump())
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@app.get("/clients/{client_id}")
def lire_client(client_id: int, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return client


@app.post("/mesures")
def recevoir_mesure(m: MesureIn, session: Session = Depends(get_session)):
    if m.client_id is not None and session.get(Client, m.client_id) is None:
        raise HTTPException(status_code=404, detail="Client introuvable")
    mesure = Mesure(**m.model_dump())
    session.add(mesure)
    session.commit()
    session.refresh(mesure)
    return mesure


@app.get("/mesures")
def lister_mesures(session: Session = Depends(get_session)):
    return session.exec(select(Mesure)).all()


@app.get("/clients/{client_id}/mesures")
def historique_client(client_id: int, session: Session = Depends(get_session)):
    if session.get(Client, client_id) is None:
        raise HTTPException(status_code=404, detail="Client introuvable")
    requete = (
        select(Mesure)
        .where(Mesure.client_id == client_id)
        .order_by(Mesure.timestamp)
    )
    return session.exec(requete).all()
