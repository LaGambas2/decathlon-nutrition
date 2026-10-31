from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


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
