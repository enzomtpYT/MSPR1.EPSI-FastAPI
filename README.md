# MSPR1.EPSI FastAPI - Backend HealthAI Coach

Backend metier FastAPI pour la plateforme HealthAI Coach.

Ce projet expose une API REST securisee (JWT), des routes CRUD metier, un endpoint analytics, et des exports CSV admin pour repondre aux besoins backend MSPR.

Au demarrage, le backend applique les migrations Alembic puis cree un utilisateur admin par defaut si DEFAULT_ADMIN_EMAIL et DEFAULT_ADMIN_PASSWORD sont definis dans l'environnement.

## Sommaire

- [Objectifs du backend](#objectifs-du-backend)
- [Stack technique](#stack-technique)
- [Architecture du projet](#architecture-du-projet)
- [Prerequis](#prerequis)
- [Configuration](#configuration)
- [Lancement local](#lancement-local)
- [Documentation API](#documentation-api)
- [Authentification](#authentification)
- [Exports CSV (compliance MSPR)](#exports-csv-compliance-mspr)
- [Migrations de base de donnees](#migrations-de-base-de-donnees)
- [Tests](#tests)
- [Deploiement Docker](#deploiement-docker)
- [Points de securite et gouvernance](#points-de-securite-et-gouvernance)
- [Limites connues et prochaines etapes](#limites-connues-et-prochaines-etapes)

## Objectifs du backend

Le backend couvre les besoins suivants:

- API REST versionnee sous `/api/v0`
- Authentification JWT
- CRUD pour utilisateurs, produits, equipements, meal logs, workout sessions, biometrics logs
- Endpoint analytics personnel
- Exports CSV admin pour la reutilisation des donnees
- Suite de tests automatisee

## Stack technique

- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL (par defaut)
- JWT via `python-jose`
- Hash mot de passe via `bcrypt`
- Tests: `pytest`, `httpx`

## Architecture du projet

```text
MSPR1.EPSI-FastAPI/
├── src/
│   ├── app.py                 # Point d'entree FastAPI
│   ├── auth.py                # JWT + securite
│   ├── config.py              # Variables d'environnement
│   ├── database.py            # Session SQLAlchemy
│   ├── schemas.py             # Schemas Pydantic
│   ├── models/                # Modeles SQLAlchemy
│   ├── router/                # Routes API
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── equipment.py
│   │   ├── meal_log.py
│   │   ├── workout_session.py
│   │   ├── biometrics_log.py
│   │   ├── analytics.py
│   │   └── exports.py         # Exports CSV admin
│   └── test/                  # Tests Pytest
└── docs/
		├── endpoints.md           # Description fonctionnelle des endpoints
		├── pytest.md              # Documentation test
		└── QUICKSTART.md          # Demarrage rapide
```

## Prerequis

- Python 3.12+
- PostgreSQL accessible
- Git

Optionnel:

- Docker (pour execution containerisee)

## Configuration

1. Copier les variables d'environnement:

```bash
cp .env.example .env
```

2. Adapter le fichier `.env` selon votre environnement:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mspr_db
SECRET_KEY=your-strong-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=adminpassword123
DEFAULT_ADMIN_IS_ADMIN=true
```

Note migration:
- Alembic utilise la meme variable `DATABASE_URL` que l'application.
- La base cible des migrations est donc PostgreSQL (ou toute URL definie dans `DATABASE_URL`).

## Lancement local

1. Creer et activer un environnement virtuel.
2. Installer les dependances.
3. Lancer l'API.

Exemple:

```bash
pip install -e ".[dev]"
fastapi dev src/app.py
```

API disponible ensuite sur:

- `http://127.0.0.1:8000`
- Prefixe metier: `/api/v0`

## Documentation API

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Documentation fonctionnelle: `docs/endpoints.md`

## Authentification

Flux standard:

1. Creer un compte via `POST /api/v0/users/`
2. Se connecter via `POST /api/v0/users/login`
3. Utiliser le token JWT:

```text
Authorization: Bearer <token>
```

## Exports CSV (compliance MSPR)

Les exports CSV sont admin uniquement.

Endpoints disponibles:

- `GET /api/v0/exports/users.csv`
- `GET /api/v0/exports/products.csv`
- `GET /api/v0/exports/equipment.csv`
- `GET /api/v0/exports/meal-logs.csv`
- `GET /api/v0/exports/workout-sessions.csv`
- `GET /api/v0/exports/biometrics-logs.csv`

Ces routes retournent:

- `Content-Type: text/csv`
- `Content-Disposition: attachment; filename="..."`

## Migrations de base de donnees

Le projet utilise Alembic pour versionner le schema.

Commandes principales:

```bash
alembic upgrade head                 # Appliquer toutes les migrations
alembic revision --autogenerate -m "message"   # Generer une nouvelle migration
alembic downgrade -1                 # Revenir d'une migration
```

Important:
- Le backend ne cree plus automatiquement les tables au demarrage.
- Il faut executer `alembic upgrade head` avant de lancer l'API sur une base vide.
- Alembic lit `DATABASE_URL` via la configuration applicative (`src/config.py`).

## Tests

Lancer la suite complete:

```bash
pytest src/test -q
```

Lancer avec couverture:

```bash
pytest src/test --cov=src --cov-report=term-missing --cov-report=html
```

Consulter aussi:

- `docs/pytest.md`

## Deploiement Docker

Un `Dockerfile` est fourni pour un deploiement simplifie, base sur l'image UV (Astral) et une installation des dependances via `uv sync --frozen --no-dev`.

### Build image

```bash
docker build -t mspr-fastapi:latest .
```

### Run container

```bash
docker run --rm -p 8000:8000 \
	-e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/mspr_db" \
	-e SECRET_KEY="change-me" \
	-e ALGORITHM="HS256" \
	-e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
	mspr-fastapi:latest
```

L'API sera disponible sur `http://localhost:8000`.

## Points de securite et gouvernance

- Mots de passe hashes avec bcrypt
- Endpoints proteges par JWT
- Gouvernance admin appliquee sur:
	- gestion globale des utilisateurs
	- ecriture produits (create/update/delete)
	- exports CSV

## Limites connues et prochaines etapes

- Le schema est actuellement cree au demarrage via SQLAlchemy.
- Pour une industrialisation complete, ajouter des migrations versionnees (Alembic) et un guide de deploiement infra complet.

