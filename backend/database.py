from sqlmodel import SQLModel, Session, create_engine

# Cet import enregistre les tables auprès de SQLModel : create_all ne crée que
# les tables déjà connues au moment où il s'exécute.
from backend import models  # noqa: F401

engine = create_engine(
    "sqlite:///nutrition.db",
    connect_args={"check_same_thread": False},
)


def creer_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
