# Inventaire des donnees et flux backend

## 1) Perimetre de ce document

Ce document couvre uniquement le backend API FastAPI du projet MSPR.

Hors perimetre volontaire:
- ETL
- Dashboard / visualisation front

Objectif:
- tracer les donnees qui entrent dans le backend,
- decrire leur stockage,
- decrire leur exposition via API JSON et exports CSV,
- expliciter les controles de securite associes.

## 2) Inventaire des domaines de donnees

### 2.1 Utilisateurs
- Entite: `users`
- Donnees principales: email, abonnement, profil sante, objectifs, contraintes
- Origine: appels API `/api/v0/users/*`
- Stockage: table relationnelle `users`
- Exposition:
  - JSON: endpoints users
  - CSV admin: `/api/v0/exports/users.csv`

### 2.2 Produits nutritionnels
- Entite: `products`
- Donnees principales: nom, macros, tags diet, categorie de prix
- Origine: CRUD API `/api/v0/products/*`
- Stockage: table `products`
- Exposition:
  - JSON: endpoints products
  - CSV admin: `/api/v0/exports/products.csv`

### 2.3 Equipements
- Entite: `equipment`
- Donnees principales: nom, categorie, localisation
- Origine: CRUD API `/api/v0/equipment/*`
- Stockage: table `equipment` + association `user_equipment`
- Exposition:
  - JSON: endpoints equipment (scope utilisateur)
  - CSV admin: `/api/v0/exports/equipment.csv`

### 2.4 Journaux repas
- Entite: `meal_logs`
- Donnees principales: utilisateur, produit, date de log
- Origine: CRUD API `/api/v0/meal-logs/*`
- Stockage: table `meal_logs`
- Exposition:
  - JSON: endpoints meal logs (scope utilisateur)
  - CSV admin: `/api/v0/exports/meal-logs.csv`

### 2.5 Sessions entrainement
- Entite: `workout_sessions`
- Donnees principales: date, bpm, duree, type, score feedback
- Origine: CRUD API `/api/v0/workout-sessions/*`
- Stockage: table `workout_sessions`
- Exposition:
  - JSON: endpoints workout sessions (scope utilisateur)
  - CSV admin: `/api/v0/exports/workout-sessions.csv`

### 2.6 Logs biometriques
- Entite: `biometrics_logs`
- Donnees principales: date, poids, sommeil, frequence cardiaque
- Origine: CRUD API `/api/v0/biometrics-logs/*`
- Stockage: table `biometrics_logs`
- Exposition:
  - JSON: endpoints biometrics logs (scope utilisateur)
  - CSV admin: `/api/v0/exports/biometrics-logs.csv`

### 2.7 Indicateurs analytics
- Entite logique: aggregation applicative
- Origine: calculs SQL agreges sur `meal_logs`, `workout_sessions`, `biometrics_logs`, `products`
- Exposition: `/api/v0/analytics/me/summary`
- Stockage: pas de table dediee (calcule a la demande)

## 3) Diagramme des flux backend

```mermaid
flowchart LR
    U[Client API: mobile/web/admin] -->|JWT login| A[/api/v0/users/login]
    U -->|CRUD| R[Routes metier /api/v0/*]

    R --> DB[(PostgreSQL)]

    DB --> R
    R -->|JSON| U

    AD[Admin authentifie] --> E[/api/v0/exports/*.csv]
    E --> DB
    E -->|CSV| AD

    R --> AN[/api/v0/analytics/me/summary]
    AN --> DB
    AN -->|JSON| U
```

## 4) Regles de securite sur les flux

- Authentification JWT obligatoire sur les routes protegees.
- Controle de role admin pour:
  - listing global users,
  - ecriture produits (create/update/delete),
  - exports CSV.
- Isolation des donnees utilisateur sur les journaux et sessions:
  - meal logs,
  - workout sessions,
  - biometrics logs,
  - equipements associes.

## 5) Regles de qualite et integrite

- Validation des payloads via schemas Pydantic.
- Controle des erreurs HTTP explicites (401, 403, 404, 422).
- Tests automatises sur:
  - auth,
  - autorisations,
  - isolation des donnees,
  - endpoints CSV.

## 6) Mapping besoins MSPR backend -> preuves projet

- API REST securisee et documentee:
  - `src/app.py`, `src/auth.py`, `docs/endpoints.md`
- Exploitation des donnees via requetes backend:
  - endpoints CRUD + analytics
- Donnees disponibles en JSON ou CSV:
  - routes JSON metier + `src/router/exports.py`
- Solution reproductible et testee:
  - `Dockerfile`, `docs/pytest.md`, suite Pytest

## 7) References internes

- Endpoints: `docs/endpoints.md`
- Tests: `docs/pytest.md`
- Quickstart: `docs/QUICKSTART.md`
- Application: `src/app.py`
- Exports: `src/router/exports.py`
