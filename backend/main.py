from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select


def maintenant():
    return datetime.now(timezone.utc)


# --- Clients ---

class ClientIn(SQLModel):
    """Ce qu'on demande au client à l'inscription."""
    pseudo: str = Field(min_length=1, max_length=50)
    annee_naissance: int = Field(ge=1920, le=2015)
    sexe: str = Field(max_length=1)          # "F" ou "M"
    taille_cm: float = Field(gt=100, lt=250)
    sport: str = Field(min_length=1)          # ex. "course", "vélo"
    heures_sport_semaine: float = Field(ge=0, le=40)
    objectif: str = Field(min_length=1)       # ex. "endurance", "perte de poids"


class Client(ClientIn, table=True):
    """Le client tel qu'il est stocké en base."""
    id: int | None = Field(default=None, primary_key=True)
    cree_le: datetime = Field(default_factory=maintenant)


# --- Mesures ---

class MesureIn(SQLModel):
    """Ce que la balance envoie."""
    scale_id: str = Field(min_length=1)
    weight_kg: float = Field(gt=20, lt=300)
    client_id: int | None = None


class Mesure(SQLModel, table=True):
    """La mesure telle qu'elle est stockée en base."""
    id: int | None = Field(default=None, primary_key=True)
    scale_id: str
    weight_kg: float
    client_id: int | None = Field(default=None, foreign_key="client.id")
    timestamp: datetime = Field(default_factory=maintenant)


# --- Base de données ---

engine = create_engine(
    "sqlite:///nutrition.db",
    connect_args={"check_same_thread": False},
)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# --- API ---

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