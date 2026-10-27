# SamaRDV — Django + Django Admin + Frontend

Application de démonstration de prise de rendez-vous médicaux. Le frontend HTML/CSS/JavaScript est adapté et renommé SamaRDV et connecté à une API Django. La base SQLite est créée localement.

## Prérequis Windows
- Python 3.12 recommandé (Python 3.11+ devrait fonctionner avec Django 5.2).
- PowerShell ou Windows Terminal.

## Installation
1. Extraire le ZIP dans `Téléchargements`.
2. Ouvrir le dossier `SamaRDV_Django`.
3. Double-cliquer sur `DEMARRER_SAMARDV.bat` ou exécuter dans PowerShell :

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations rdv
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Si `py -3.12` n'existe pas, utilisez `py -3` à la place. Si PowerShell bloque l'activation, les commandes `python -m ...` et `pip install ...` peuvent être lancées sans activer le venv en utilisant `.venv\Scripts\python.exe`.

## Créer l'administrateur
Dans un deuxième terminal, depuis le dossier du projet :

```powershell
.venv\Scripts\python.exe manage.py createsuperuser
```

Saisissez le nom d'utilisateur, l'e-mail et le mot de passe. Vous pouvez aussi double-cliquer sur `CREER_ADMIN.bat`.

## Adresses locales
- Site : http://127.0.0.1:8000/
- Administration Django : http://127.0.0.1:8000/admin/
- Santé API : http://127.0.0.1:8000/api/sante

Le serveur Django sert également les fichiers du frontend. Il n'est donc pas nécessaire de démarrer `python -m http.server 5500`.

## Fonctionnalités incluses
- Administration Django des utilisateurs, hôpitaux, spécialités, médecins, rendez-vous et messages de contact.
- API JSON compatible avec les appels utilisés par le frontend : catalogue, statistiques, inscription/connexion par jeton, créneaux, réservation, suivi et annulation.
- Données de démonstration Sénégal ajoutées par `python manage.py seed_demo`.
- SQLite pour démarrer facilement en local.

## Notes importantes
- Il s'agit d'une base de développement/formation, pas d'un système prêt à gérer de vraies données médicales en production.
- Avant tout déploiement public, remplacez `SECRET_KEY`, désactivez `DEBUG`, configurez HTTPS, les sauvegardes, les règles d'accès et les tests de sécurité.
- Les créneaux de démonstration sont générés de 09 h à 17 h. Adaptez les horaires au fonctionnement réel des établissements.
- Les comptes patients créés depuis le site peuvent se connecter au frontend ; les comptes administrateurs se créent via `createsuperuser`.
