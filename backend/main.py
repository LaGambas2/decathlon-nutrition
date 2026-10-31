from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select


# --- Modèles ---

class MesureIn(SQLModel):
    """Ce que la balance envoie."""
    scale_id: str
    weight_kg: float


class Mesure(SQLModel, table=True):
    """Ce qu'on stocke en base (avec un id et la date en plus)."""
    id: int | None = Field(default=None, primary_key=True)
    scale_id: str
    weight_kg: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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


@app.post("/mesures")
def recevoir_mesure(m: MesureIn, session: Session = Depends(get_session)):
    mesure = Mesure(**m.model_dump())
    session.add(mesure)
    session.commit()
    session.refresh(mesure)
    return mesure


@app.get("/mesures")
def lister_mesures(session: Session = Depends(get_session)):
    return session.exec(select(Mesure)).all()