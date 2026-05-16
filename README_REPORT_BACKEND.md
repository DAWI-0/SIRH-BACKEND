# Rapport Technique Backend - SIRH (Système d'Information Ressources Humaines)

## 1. Backend Overview
Le backend de ce projet SIRH (Système d'Information Ressources Humaines) est développé pour centraliser, gérer et automatiser les processus vitaux des ressources humaines d'une entreprise.
Ses principales responsabilités incluent :
- **Gestion Administrative** : Stockage et traitement des données des employés, des contrats, et des départements.
- **Gestion des Temps et Activités (GTA)** : Suivi des présences via des pointages IoT (RFID/ESP32) et gestion manuelle des présences/absences.
- **Gestion de la Paie** : Calcul automatisé des fiches de paie basé sur le salaire de base, les absences et les heures supplémentaires.
- **Gestion des Congés** : Workflows de demande et de validation des congés.
- **Communication en Temps Réel** : Système de messagerie instantanée (Chat) entre les employés et les responsables RH.
- **Dashboard Analytique** : Fourniture de KPIs et de statistiques en temps réel pour l'aide à la décision.

## 2. Technologies Used
- **Framework Principal** : Django (v6.0.3)
- **API REST** : Django REST Framework (DRF)
- **Base de Données** : PostgreSQL
- **Temps Réel / WebSockets** : Django Channels & Daphne
- **Broker de Messages (WebSocket)** : Redis
- **Authentification** : JWT (JSON Web Tokens via `rest_framework_simplejwt`)
- **IoT & Messagerie** : Paho MQTT (Connexion avec HiveMQ pour la remontée des données capteurs)
- **CORS** : `django-cors-headers` pour la communication sécurisée avec le frontend React.
- **Conteneurisation (Services tiers)** : Docker Compose (PostgreSQL, Redis)

## 3. Backend Architecture
L'architecture globale repose sur le modèle **MVT (Model-View-Template)** de Django, mais utilisé ici de manière découplée (Headless) pour agir uniquement comme un serveur d'API RESTful et un serveur WebSocket.

### Architecture Modulaire
Le système est divisé en plusieurs applications (Apps) Django, chacune ayant une responsabilité unique (Single Responsibility Principle) :
- `core` : Configuration globale du projet.
- `accounts` : Utilisateurs, rôles, permissions et historique/archives.
- `organization` : Structure de l'entreprise (Départements, Projets).
- `attendance` : Traitement des données brutes de pointage (IoT).
- `payroll` : Contrats, présences manuelles, congés et calculs de paie.
- `chat` : Logique conversationnelle et temps réel.

### Flux de Requête (Request Flow)
1. Le Frontend React envoie une requête HTTP (REST) avec un token JWT dans les headers.
2. Le `CorsMiddleware` et les middlewares d'authentification valident la requête.
3. Le routeur (`urls.py`) dirige vers la vue (`views.py`) appropriée.
4. La vue vérifie les permissions (ex: `IsAdminOrRH`).
5. La vue interroge la base de données via l'ORM et sérialise la donnée (`serializers.py`).
6. La réponse JSON est retournée au frontend.

## 4. Project Structure
- `core/` : Contient `settings.py` (configuration), `urls.py` (routeur principal), et `asgi.py` (point d'entrée pour les WebSockets et Daphne).
- `accounts/` : Contient les modèles `Utilisateur`, `Employe` et `ArchiveEmploye`. Gère l'authentification et les KPIs du dashboard.
- `organization/` : Contient `Departement` et `Projet`.
- `attendance/` : Contient `PointageIoT` pour enregistrer les scans RFID.
- `payroll/` : Cœur de la gestion RH avec `FichePaie`, `PresenceManuelle`, `Conge`, et `Contrat`.
- `chat/` : Contient les modèles `Conversation` et `Message` ainsi que la logique WebSocket.
- `bridge_mqtt.py` : Script Python indépendant (Daemon) qui écoute le broker MQTT (HiveMQ) et injecte directement les pointages IoT dans l'ORM Django.
- `seed.py` / `seed_mois.py` : Scripts de peuplement (seeding) massif pour initialiser la base de données avec des données de test réalistes.

## 5. Database Architecture
La base de données PostgreSQL est structurée de manière relationnelle autour du modèle central `Employe`.

### Modèles Principaux et Relations
- **Utilisateur (AbstractUser)** : Modèle parent personnalisé. Les rôles (`ADMIN`, `RH`, `EMPLOYE`) y sont définis.
- **Employe (Hérite d'Utilisateur)** : Ajoute le `matricule`, le `statut`, le `solde_conges`, etc.
  - *Relation* : `ForeignKey` vers `organization.Departement`.
- **Departement** :
  - *Relation* : `OneToOneField` vers `Employe` (le manager du département).
- **ArchiveEmploye** : Table de log pour garder la trace des employés ayant quitté l'entreprise (démission, licenciement).
- **PointageIoT** :
  - *Relation* : `ForeignKey` vers `Employe`.
- **PresenceManuelle** : Résumé journalier (Présent, Absent, Repos, Heures Supp).
  - *Relation* : `ForeignKey` vers `Employe` (`unique_together` avec la date).
- **Conge** / **Contrat** / **FichePaie** :
  - *Relation* : Tous ont une `ForeignKey` vers `Employe`.
- **Conversation** :
  - *Relations* : Deux `ForeignKey` vers Utilisateur (un `employee` et un `hr`).
- **Message** :
  - *Relations* : `ForeignKey` vers `Conversation` et `ForeignKey` vers l'expéditeur (`Utilisateur`).

## 6. Main Functionalities
- **Gestion des Employés & Archiving** : Opérations CRUD complètes. Lors du départ d'un employé (ex: licenciement), son compte actif est supprimé mais ses données sont transférées vers `ArchiveEmploye`. Un Webhook (via `n8n`) est également déclenché.
- **Statistiques Dashboard** : Une vue complexe (`DashboardStatsView`) calcule en temps réel la masse salariale, le taux de présence, et la répartition des contrats via l'ORM (utilisation de `Count`, `Sum`, `aggregate`).
- **Gestion des Présences** : Système hybride avec des pointages automatiques (via `bridge_mqtt.py` qui simule l'IoT) et un contrôle manuel des RH (`PresenceManuelle`).
- **Génération des Fiches de Paie** : Moteur de calcul qui prend le salaire de base, déduit les jours `ABSENT`, ajoute les primes des jours `SUPP` et génère automatiquement les `FichePaie` pour le mois sélectionné.
- **Messagerie Interne** : Création de conversations uniques entre RH et Employés avec historique et distribution asynchrone des messages.

## 7. Authentication & Security
- **JWT (JSON Web Tokens)** : L'application utilise `SimpleJWT`. Le payload du token a été surchargé (`CustomTokenObtainPairSerializer`) pour y inclure le rôle de l'utilisateur, son nom, et un booléen `is_chef` limitant ainsi le besoin de requêtes supplémentaires côté frontend.
- **Permissions DRF** : Mise en place de permissions granulaires :
  - `IsAuthenticated` (Général)
  - Des permissions personnalisées (logiques) interdisant à un employé classique d'accéder aux contrats d'autres employés ou de valider ses propres congés.
- **Mot de passe** : Hachage sécurisé géré par `AbstractUser` de Django (PBKDF2 par défaut).
- **Contrôle d'accès** : Les vues filtrent automatiquement les `querysets`. Un employé ne voit que *ses* congés ou *ses* fiches de paie (via `self.request.user`).

## 8. REST API System
Le système expose de multiples endpoints JSON :
- **Accounts** : `/api/accounts/employes/`, `/api/accounts/archives/`, `/api/accounts/dashboard-stats/`
- **Auth** : `/api/token/`, `/api/token/refresh/`
- **Payroll** : `/api/payroll/generer-paie/` (POST pour le calcul), `/api/payroll/conges/`, `/api/payroll/presences-manuelles/toggle/`
- **Attendance** : `/api/attendance/pointages/`
- **Organization** : `/api/organization/departements/` (Utilisation de ViewSets et Routers DRF)

**Flux typique (ex: Génération Paie)** :
Le client POST la demande avec `mois` et `annee`. La vue itère sur les employés actifs, lit leurs `PresenceManuelle` de ce mois-là, fait les calculs arithmétiques via `Decimal` pour éviter les erreurs de flottants, enregistre les fiches et retourne le total généré.

## 9. WebSocket & Real-Time Chat
Pour le module de Chat, le protocole HTTP classique est remplacé/complété par **WebSockets** :
- **Django Channels** agit comme interface asynchrone (ASGI).
- **Redis Channel Layer** est utilisé comme broker en arrière-plan pour distribuer les messages (Events) aux différents consommateurs connectés.
- Lorsqu'un message est envoyé, il est enregistré dans PostgreSQL via l'API, puis Django Channels notifie instantanément le destinataire connecté à la Room correspondante, évitant tout "Long Polling".

## 10. Database Management
- **ORM Django** : Toutes les requêtes SQL sont abstraites par l'ORM. 
- **Optimisation** : Utilisation de `.select_related()` (ex: dans les congés en attente) pour optimiser les requêtes SQL et éviter le problème "N+1 queries".
- **Migrations** : Les évolutions de la base (ex: passage à des UUID comme clés primaires) sont gérées par le système robuste de `makemigrations` / `migrate`.

## 11. Configuration
- **settings.py** : Fichier central. Configure PostgreSQL (`DATABASES`), Redis (`CHANNEL_LAYERS`), les applications installées (`INSTALLED_APPS`), et les variables de sécurité.
- L'application asynchrone est déclarée via `ASGI_APPLICATION = 'core.asgi.application'` pour Daphne.
- **Docker** : Utilisation d'un fichier `docker-compose.yml` pour provisionner rapidement l'environnement base de données (PostgreSQL sur port 5432) et le cache/broker (Redis sur port 6379).

## 12. Challenges Encountered
1. **Concurrence & IoT** : Gérer la réception en temps réel de dizaines de pointages IoT depuis le broker HiveMQ vers la base de données locale sans bloquer l'application principale. Résolu par l'utilisation d'un daemon externe (`bridge_mqtt.py`).
2. **Calculs financiers fiables** : Mettre au point la formule du salaire tenant compte des jours ouvrables variables (environ 26 jours) et intercepter de manière sécurisée les valeurs non numériques. Résolu par l'utilisation stricte du module `Decimal` et un bloc `try/except` dans `payroll/views.py`.
3. **Circular Dependencies** : Lier les départements aux managers (Employes) et les Employes aux départements sans créer de boucle d'import infini. Résolu en utilisant les noms de chaînes de caractères (ex: `'organization.Departement'`) dans les `ForeignKey`.
4. **Transition Synchrone/Asynchrone** : Assurer la cohabitation entre DRF (largement synchrone) et Django Channels (asynchrone).

## 13. Future Improvements
- **Sécurité** : Migrer toutes les informations d'identification (clés secrètes Django, mots de passe DB, accès HiveMQ) de `settings.py` et du code vers un fichier `.env` non suivi par Git.
- **Tâches Asynchrones (Workers)** : Mettre en place `Celery` ou `RQ` pour déléguer la génération de centaines de fiches de paie dans une file d'attente en arrière-plan, évitant un timeout HTTP.
- **Tests Automatisés** : Ajouter une suite de tests unitaires (`pytest` ou `django.test`) couvrant au moins les fonctions critiques de paie et de validation des congés.
- **Mise en Cache** : Cacher la réponse JSON de `DashboardStatsView` dans Redis pour réduire la charge sur PostgreSQL, avec invalidation par événements.

## 14. Installation Guide
1. **Cloner le dépôt et initialiser l'environnement virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Mac/Linux
   # venv\Scripts\activate   # Sur Windows
   ```
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer les services externes (PostgreSQL & Redis)** :
   ```bash
   docker-compose up -d
   ```
4. **Appliquer les migrations** :
   ```bash
   python manage.py migrate
   ```
5. **Peupler la base de données** (Création des employés, congés, historique paie) :
   ```bash
   python seed.py
   python seed_mois.py
   ```
6. **Lancer le serveur de développement (Daphne/Channels gérés auto)** :
   ```bash
   python manage.py runserver
   ```
7. **Lancer le script de pointage IoT (Dans un autre terminal)** :
   ```bash
   python bridge_mqtt.py
   ```
L'API sera disponible sur `http://127.0.0.1:8000/`.
