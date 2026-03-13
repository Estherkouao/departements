# Gestion Departements Django App

## Local Development
```bash
cd /home/esther/Bureau/departements
python app/manage.py migrate
python app/manage.py createsuperuser
python app/manage.py runserver
```
Access: http://127.0.0.1:8000/

## Docker
Add docker-compose.yml:
```
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data/

  app:
    build: .
    ports:
      - '8000:8000'
    env_file: .env
    depends_on:
      - db
    volumes:
      - app/media/:/app/media/

volumes:
  postgres_data:
```

Run: `docker-compose up --build`

## Structure
- app/: Django project (manage.py, config/, GestionDepartement/)
- templates/static/media under app/


