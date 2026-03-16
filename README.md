
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows

#Installer les dépendances


pip install -r requirements.txt

# Supprimer les anciens conteneurs

docker rm -f departements_app pg_departements

# Installer les dépendances

pip install -r requirements.txt


## pour cree l'image docker

# Lancer PostgreSQL

docker run -d \
  --name pg_departements \
  --network departements_net \
  -e POSTGRES_USER=esther \
  -e POSTGRES_PASSWORD=123456 \
  -e POSTGRES_DB=departements \
  postgres:17

# Lancer Django

docker run -d \
  --name departements_app \
  --network departements_net \
  -p 8001:8000 \
  -v $(pwd)/app:/app \
  -w /app \
  departements


# Vérifier les logs

docker logs -f departements_app

