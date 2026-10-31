import random
import time
import requests

API_URL = "http://127.0.0.1:8000/mesures"
SCALE_ID = "balance-bussigny-01"
NOMBRE_DE_MESURES = 10
PAUSE_SECONDES = 1


def generer_poids():
    """Poids réaliste d'un adulte, avec de temps en temps une valeur aberrante."""
    if random.random() < 0.1:
        return random.choice([0.0, 450.0])  # simule un bug de capteur
    return round(random.gauss(72, 12), 1)


def envoyer_mesure(poids):
    donnees = {"scale_id": SCALE_ID, "weight_kg": poids}
    try:
        reponse = requests.post(API_URL, json=donnees, timeout=5)
    except requests.ConnectionError:
        print("Serveur injoignable : as-tu lancé uvicorn ?")
        return

    if reponse.status_code == 200:
        print(f"OK     {poids:6.1f} kg -> id {reponse.json()['id']}")
    else:
        print(f"REFUS  {poids:6.1f} kg -> code {reponse.status_code}")


if __name__ == "__main__":
    for _ in range(NOMBRE_DE_MESURES):
        envoyer_mesure(generer_poids())
        time.sleep(PAUSE_SECONDES)