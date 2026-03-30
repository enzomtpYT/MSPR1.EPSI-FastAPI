# Documentation des Endpoints API

## Base URL
- Prefixe global: `/api/v0`
- Authentification: `Authorization: Bearer <token>` pour tous les endpoints proteges

## Convention de lecture
- Entree: body JSON et/ou query params
- Sortie: JSON retourne en cas de succes
- Erreurs courantes: principaux codes HTTP

---

## 1) Utilisateurs

### POST /users/
Creer un utilisateur.

Entree (JSON):
```json
{
  "User_mail": "alice@example.com",
  "User_password": "Secret123!",
  "isAdmin": false,
  "User_Subscription": "free",
  "User_age": 25,
  "User_weight": 65.5,
  "User_Height": 170.0,
  "User_gender": "F",
  "User_Goals": "Perte de poids",
  "User_Allergies": "Arachides",
  "User_Dietary_Preferences": "Vegetarien",
  "User_Budget_Level": "Moyen",
  "User_Injuries": "Genou"
}
```

Sortie (201):
```json
{
  "User_ID": 1,
  "User_mail": "alice@example.com",
  "isAdmin": false,
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z",
  "User_Subscription": "free",
  "User_age": 25,
  "User_weight": 65.5,
  "User_Height": 170.0,
  "User_gender": "F",
  "User_Goals": "Perte de poids",
  "User_Allergies": "Arachides",
  "User_Dietary_Preferences": "Vegetarien",
  "User_Budget_Level": "Moyen",
  "User_Injuries": "Genou"
}
```

Erreurs courantes:
- 400: email deja utilise
- 422: payload invalide

### POST /users/login
Connexion utilisateur (JWT).

Entree (JSON):
```json
{
  "User_mail": "alice@example.com",
  "User_password": "Secret123!"
}
```

Sortie (200):
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

Erreurs courantes:
- 401: identifiants invalides

### GET /users/
Lister les utilisateurs (admin uniquement).

Entree:
- Query params: `skip` (defaut 0), `limit` (defaut 100)
- Header JWT requis

Sortie (200):
```json
[
  {
    "User_ID": 1,
    "User_mail": "alice@example.com",
    "isAdmin": false,
    "created_at": "2026-03-30T10:00:00Z",
    "updated_at": "2026-03-30T10:00:00Z"
  }
]
```

Erreurs courantes:
- 401: token absent/invalide
- 403: utilisateur non admin

### GET /users/me
Recuperer le profil de l'utilisateur connecte.

Entree:
- Header JWT requis

Sortie (200):
```json
{
  "User_ID": 1,
  "User_mail": "alice@example.com",
  "isAdmin": false,
  "created_at": "2026-03-30T10:00:00Z",
  "updated_at": "2026-03-30T10:00:00Z"
}
```

Erreurs courantes:
- 401: token absent/invalide

### GET /users/{user_id}
Consulter un utilisateur (soi-meme ou admin).

Entree:
- Path param: `user_id`
- Header JWT requis

Sortie (200): objet `UserRead`.

Erreurs courantes:
- 401: token absent/invalide
- 403: acces refuse
- 404: utilisateur introuvable

### PUT /users/{user_id}
Modifier un utilisateur (soi-meme ou admin).

Entree:
- Path param: `user_id`
- Header JWT requis
- Body JSON: meme schema que creation (`UserCreate`)

Sortie (200): objet `UserRead` mis a jour.

Erreurs courantes:
- 401: token absent/invalide
- 403: acces refuse
- 404: utilisateur introuvable
- 422: payload invalide

### DELETE /users/{user_id}
Supprimer un utilisateur (soi-meme ou admin).

Entree:
- Path param: `user_id`
- Header JWT requis

Sortie (204): vide.

Erreurs courantes:
- 401: token absent/invalide
- 403: acces refuse
- 404: utilisateur introuvable

---

## 2) Produits

### POST /products/
Creer un produit (admin uniquement).

Entree (JSON):
```json
{
  "product_name": "Poulet",
  "product_kcal": 165,
  "product_protein": 31,
  "product_carbs": 0,
  "product_fat": 3.6,
  "product_fiber": 0,
  "product_sugar": 0,
  "product_sodium": 74,
  "product_chol": 85,
  "Product_Diet_Tags": "high-protein",
  "Product_Price_Category": "medium"
}
```

Sortie (201): objet `ProductRead`.

Erreurs courantes:
- 401: token absent/invalide
- 403: utilisateur non admin
- 422: payload invalide

### GET /products/
Lister les produits.

Entree:
- Header JWT requis
- Query params: `skip`, `limit`

Sortie (200): liste de `ProductRead`.

Erreurs courantes:
- 401: token absent/invalide

### GET /products/{product_id}
Recuperer un produit par id.

Entree:
- Path param: `product_id`
- Header JWT requis

Sortie (200): objet `ProductRead`.

Erreurs courantes:
- 401: token absent/invalide
- 404: produit introuvable

### PUT /products/{product_id}
Modifier un produit (admin uniquement).

Entree:
- Path param: `product_id`
- Header JWT requis
- Body JSON: `ProductCreate`

Sortie (200): objet `ProductRead` mis a jour.

Erreurs courantes:
- 401: token absent/invalide
- 403: utilisateur non admin
- 404: produit introuvable

### DELETE /products/{product_id}
Supprimer un produit (admin uniquement).

Entree:
- Path param: `product_id`
- Header JWT requis

Sortie (204): vide.

Erreurs courantes:
- 401: token absent/invalide
- 403: utilisateur non admin
- 404: produit introuvable

---

## 3) Equipements

### POST /equipment/
Creer un equipement et l'associer a l'utilisateur connecte.

Entree (JSON):
```json
{
  "Equipment_Name": "Tapis de course",
  "Equipment_Category": "Cardio",
  "Equipment_Location": "Maison"
}
```

Sortie (201): objet `EquipmentRead`.

Erreurs courantes:
- 401: token absent/invalide
- 422: payload invalide

### GET /equipment/
Lister les equipements de l'utilisateur connecte.

Entree:
- Header JWT requis
- Query params: `skip`, `limit`

Sortie (200): liste de `EquipmentRead`.

Erreurs courantes:
- 401: token absent/invalide

### GET /equipment/{equipment_id}
Recuperer un equipement si l'utilisateur y a acces.

Entree:
- Path param: `equipment_id`
- Header JWT requis

Sortie (200): objet `EquipmentRead`.

Erreurs courantes:
- 401: token absent/invalide
- 403: acces refuse
- 404: equipement introuvable

### PUT /equipment/{equipment_id}
Modifier un equipement si l'utilisateur y a acces.

Entree:
- Path param: `equipment_id`
- Header JWT requis
- Body JSON: `EquipmentCreate`

Sortie (200): objet `EquipmentRead` mis a jour.

Erreurs courantes:
- 401: token absent/invalide
- 403: acces refuse
- 404: equipement introuvable

### DELETE /equipment/{equipment_id}
Retirer l'association entre utilisateur et equipement.

Entree:
- Path param: `equipment_id`
- Header JWT requis

Sortie (204): vide.

Erreurs courantes:
- 401: token absent/invalide
- 403: acces refuse
- 404: equipement introuvable

---

## 4) Journal des repas

### POST /meal-logs/
Creer un log repas pour l'utilisateur connecte.

Entree (JSON):
```json
{
  "User_ID": 999,
  "Product_ID": 1,
  "Log_Date": "2026-03-30"
}
```

Note: `User_ID` du payload est ecrase par l'utilisateur connecte.

Sortie (201): objet `MealLogRead`.

Erreurs courantes:
- 401: token absent/invalide
- 422: payload invalide

### GET /meal-logs/
Lister les logs repas de l'utilisateur connecte.

Entree:
- Header JWT requis
- Query params: `skip`, `limit`

Sortie (200): liste de `MealLogRead`.

Erreurs courantes:
- 401: token absent/invalide

### GET /meal-logs/{log_id}
Recuperer un log repas appartenant a l'utilisateur connecte.

Entree:
- Path param: `log_id`
- Header JWT requis

Sortie (200): objet `MealLogRead`.

Erreurs courantes:
- 401: token absent/invalide
- 404: log introuvable

### PUT /meal-logs/{log_id}
Modifier un log repas appartenant a l'utilisateur connecte.

Entree:
- Path param: `log_id`
- Header JWT requis
- Body JSON: `MealLogCreate`

Sortie (200): objet `MealLogRead` mis a jour.

Erreurs courantes:
- 401: token absent/invalide
- 404: log introuvable

### DELETE /meal-logs/{log_id}
Supprimer un log repas appartenant a l'utilisateur connecte.

Entree:
- Path param: `log_id`
- Header JWT requis

Sortie (204): vide.

Erreurs courantes:
- 401: token absent/invalide
- 404: log introuvable

---

## 5) Sessions d'entrainement

### POST /workout-sessions/
Creer une session pour l'utilisateur connecte.

Entree (JSON):
```json
{
  "User_ID": 999,
  "Session_Date": "2026-03-30",
  "Session_MaxBpm": 180,
  "Session_AvgBpm": 145,
  "Session_RestingBpm": 60,
  "Session_Duration": 50,
  "Session_Type": "Cardio",
  "User_Feedback_Score": 8
}
```

Note: `User_ID` du payload est ecrase par l'utilisateur connecte.

Sortie (201): objet `WorkoutSessionRead`.

Erreurs courantes:
- 401: token absent/invalide
- 422: payload invalide

### GET /workout-sessions/
Lister les sessions de l'utilisateur connecte.

Entree:
- Header JWT requis
- Query params: `skip`, `limit`

Sortie (200): liste de `WorkoutSessionRead`.

Erreurs courantes:
- 401: token absent/invalide

### GET /workout-sessions/{session_id}
Recuperer une session appartenant a l'utilisateur connecte.

Entree:
- Path param: `session_id`
- Header JWT requis

Sortie (200): objet `WorkoutSessionRead`.

Erreurs courantes:
- 401: token absent/invalide
- 404: session introuvable

### PUT /workout-sessions/{session_id}
Modifier une session appartenant a l'utilisateur connecte.

Entree:
- Path param: `session_id`
- Header JWT requis
- Body JSON: `WorkoutSessionCreate`

Sortie (200): objet `WorkoutSessionRead` mis a jour.

Erreurs courantes:
- 401: token absent/invalide
- 404: session introuvable

### DELETE /workout-sessions/{session_id}
Supprimer une session appartenant a l'utilisateur connecte.

Entree:
- Path param: `session_id`
- Header JWT requis

Sortie (204): vide.

Erreurs courantes:
- 401: token absent/invalide
- 404: session introuvable

---

## 6) Journal biometrique

### POST /biometrics-logs/
Creer un log biometrique pour l'utilisateur connecte.

Entree (JSON):
```json
{
  "User_ID": 999,
  "Log_Date": "2026-03-30",
  "Weight": 64.2,
  "Sleep_Hours": 7.5,
  "Heart_Rate": 58
}
```

Note: `User_ID` du payload est ecrase par l'utilisateur connecte.

Sortie (201): objet `BiometricsLogRead`.

Erreurs courantes:
- 401: token absent/invalide
- 422: payload invalide

### GET /biometrics-logs/
Lister les logs biometriques de l'utilisateur connecte.

Entree:
- Header JWT requis
- Query params: `skip`, `limit`

Sortie (200): liste de `BiometricsLogRead`.

Erreurs courantes:
- 401: token absent/invalide

### GET /biometrics-logs/{log_id}
Recuperer un log biometrique appartenant a l'utilisateur connecte.

Entree:
- Path param: `log_id`
- Header JWT requis

Sortie (200): objet `BiometricsLogRead`.

Erreurs courantes:
- 401: token absent/invalide
- 404: log introuvable

### PUT /biometrics-logs/{log_id}
Modifier un log biometrique appartenant a l'utilisateur connecte.

Entree:
- Path param: `log_id`
- Header JWT requis
- Body JSON: `BiometricsLogCreate`

Sortie (200): objet `BiometricsLogRead` mis a jour.

Erreurs courantes:
- 401: token absent/invalide
- 404: log introuvable

### DELETE /biometrics-logs/{log_id}
Supprimer un log biometrique appartenant a l'utilisateur connecte.

Entree:
- Path param: `log_id`
- Header JWT requis

Sortie (204): vide.

Erreurs courantes:
- 401: token absent/invalide
- 404: log introuvable

---

## 7) Analytics

### GET /analytics/me/summary
Retourne un resume analytics de l'utilisateur connecte.

Entree:
- Header JWT requis

Sortie (200):
```json
{
  "user_id": 1,
  "meal_logs_count": 12,
  "workout_sessions_count": 8,
  "biometrics_logs_count": 6,
  "total_logged_kcal": 2450.0,
  "avg_workout_duration_minutes": 47.5,
  "avg_sleep_hours": 7.2,
  "latest_weight": 64.1
}
```

Erreurs courantes:
- 401: token absent/invalide
