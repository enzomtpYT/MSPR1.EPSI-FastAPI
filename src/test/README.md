# Suite de tests FastAPI

## Objectif
Cette suite valide les points critiques de l'API :
- disponibilite de l'application,
- authentification et autorisations,
- operations CRUD sur les utilisateurs et les produits,
- reponses d'erreur attendues (401, 403, 404, 422).

## Tests par fichier

### test_app.py (5 tests)
- `test_app_startup` : verifie que l'application demarre et repond.
- `test_health_check_if_exists` : verifie l'endpoint de sante s'il est expose.
- `test_api_prefix_v0` : verifie que les routes sont servies sous `/api/v0`.
- `test_invalid_endpoint` : verifie qu'une route inconnue retourne `404`.
- `test_response_has_headers` : verifie la presence des en-tetes HTTP standards.

### test_user.py (15 tests)

Creation d'utilisateur :
- `test_create_user_success` : cree un utilisateur avec des donnees valides.
- `test_create_user_duplicate_email` : refuse un email deja utilise.
- `test_create_user_missing_email` : refuse une requete sans email.
- `test_create_user_missing_password` : refuse une requete sans mot de passe.

Connexion :
- `test_login_success` : retourne un token JWT avec des identifiants valides.
- `test_login_invalid_email` : refuse la connexion avec un email inconnu.
- `test_login_invalid_password` : refuse la connexion avec un mauvais mot de passe.

Liste des utilisateurs et permissions :
- `test_get_users_unauthorized` : bloque l'acces sans authentification.
- `test_get_users_non_admin` : bloque un utilisateur authentifie non admin.
- `test_get_users_admin` : autorise un utilisateur admin.

Utilisateur courant :
- `test_get_current_user_success` : retourne le profil de l'utilisateur authentifie.
- `test_get_current_user_unauthorized` : refuse l'acces sans token.

Utilisateur par id et confidentialite :
- `test_get_user_self` : autorise un utilisateur a lire son propre profil.
- `test_get_user_other_unauthorized` : empeche un utilisateur de lire le profil d'un autre.
- `test_get_user_admin_can_view_any` : autorise un admin a lire n'importe quel profil.

### test_product.py (14 tests)

Creation de produit :
- `test_create_product_success` : cree un produit avec un payload complet.
- `test_create_product_unauthorized` : bloque la creation sans authentification.
- `test_create_product_minimal` : cree un produit avec les champs minimaux requis.
- `test_create_product_missing_name` : refuse la creation sans nom de produit.

Liste des produits :
- `test_get_products_unauthorized` : bloque l'acces sans authentification.
- `test_get_products_success` : retourne la liste des produits.
- `test_get_products_pagination` : verifie la limite via le parametre `limit`.
- `test_get_products_with_skip` : verifie le decalage via le parametre `skip`.

Produit par id :
- `test_get_product_success` : retourne le produit demande.
- `test_get_product_not_found` : retourne `404` si l'id n'existe pas.
- `test_get_product_unauthorized` : bloque l'acces sans authentification.

Mise a jour de produit :
- `test_update_product_success` : met a jour les champs d'un produit.
- `test_update_product_unauthorized` : bloque la mise a jour sans authentification.
- `test_update_product_not_found` : retourne `404` si le produit n'existe pas.

## Lancer les tests

```bash
pytest src/test/ -v
```

