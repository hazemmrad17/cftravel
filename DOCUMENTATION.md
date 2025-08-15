# Documentation Complète - Projet CFTravel

## Vue d'ensemble du Projet

CFTravel est une application web hybride qui combine une interface utilisateur Symfony (PHP) avec un backend d'intelligence artificielle Python pour fournir des recommandations de voyage personnalisées. Le projet utilise une architecture microservices avec un agent spécialisé : Asia.fr (agent spécialisé pour les destinations asiatiques).

## Architecture Technique

### Stack Technologique

**Backend Frontend (Symfony)**
- PHP 8.1+
- Symfony 6.4
- Doctrine ORM
- Twig Templates
- Webpack Encore

**Backend IA (Python)**
- FastAPI
- Groq (LLM API)
- LangChain
- Sentence Transformers
- NumPy/SciPy
- BeautifulSoup4

**Frontend**
- JavaScript ES6+
- Alpine.js
- Lucide Icons
- Tailwind CSS
- Stimulus

### Ports Utilisés
- Port 8000 : API Python (FastAPI)
- Port 8001 : Application Symfony

## Modèles IA et Capacités

### Modèles Groq Utilisés

**GPT-OSS-120B (Modèle Principal)**
- **Identifiant** : `gpt-oss-120b`
- **Capacités** : Modèle open source de 120 milliards de paramètres
- **Contexte** : Large contexte pour les conversations complexes
- **Vitesse** : Réponses ultra-rapides grâce aux LPU de Groq
- **Utilisation** : Traitement principal des requêtes utilisateur
- **Avantages** : Modèle open source récemment libéré, performances élevées

**Kimi K2 (Modèle Secondaire)**
- **Identifiant** : `kimi-k2`
- **Capacités** : Modèle de 1 trillion de paramètres (1T)
- **Contexte** : Contexte extrêmement large pour l'analyse approfondie
- **Utilisation** : Traitement des requêtes complexes nécessitant une compréhension profonde
- **Avantages** : Modèle le plus puissant disponible, récemment open source
- **Particularité** : Premier modèle de 1T paramètres accessible via API

**Llama 3 8B (Modèle de Fallback)**
- **Identifiant** : `llama3-8b-8192`
- **Capacités** : Modèle léger et rapide
- **Utilisation** : Fallback en cas de problème avec les modèles principaux
- **Contexte** : 8192 tokens pour les conversations longues
- **Avantages** : Fiabilité et stabilité éprouvées

### Choix Technologique : Modèles Open Source Récents

**GPT-OSS-120B (Modèle Principal)**
- **Libération Récente** : Modèle open source de 120B paramètres
- **Performance** : Qualité comparable aux modèles propriétaires
- **Flexibilité** : Contrôle total sur l'utilisation et la personnalisation
- **Coût** : Tarification optimisée via Groq

**Kimi K2 (1T Paramètres)**
- **Révolution Technologique** : Premier modèle de 1 trillion de paramètres accessible
- **Capacités Exceptionnelles** : Compréhension et raisonnement de niveau humain
- **Libération Open Source** : Accès démocratisé aux modèles les plus avancés
- **Utilisation Spécialisée** : Pour les analyses complexes et les recommandations sophistiquées

### Choix Technologique : Groq

**Pourquoi Groq ?**
- **LPU Technology** : Processeurs spécialisés pour le langage naturel
- **Latence Ultra-faible** : Réponses en millisecondes, même pour les modèles géants
- **Scalabilité** : Infrastructure capable de gérer les modèles de 1T paramètres
- **Modèles Open Source** : Support des derniers modèles libérés
- **Coût Optimisé** : Tarification compétitive pour les applications en production

**Avantages par rapport aux autres fournisseurs :**
- **Vitesse** : 10-100x plus rapide que les alternatives
- **Fiabilité** : Infrastructure dédiée aux LLM
- **Flexibilité** : Support de multiples modèles open source
- **Développement** : API simple et intuitive
- **Modèles Géants** : Capacité à exécuter des modèles de 1T paramètres

## Web Scraping et Base de Données

### Processus de Collecte de Données

Le projet utilise des scripts de web scraping personnalisés pour collecter et enrichir les données de voyage asiatiques.

**Scripts Principaux :**
- `scripts/scrape_asia_enhanced_auto.py` : Scraping automatique des destinations asiatiques
- `scripts/merge_enhanced_data.py` : Fusion et enrichissement des données

**Technologies de Scraping :**
- **BeautifulSoup4** : Parsing HTML et extraction de contenu structuré
- **Requests** : Requêtes HTTP pour récupérer les pages web
- **Pandas** : Traitement et manipulation des données tabulaires
- **NumPy** : Calculs numériques pour la génération de prix

### Enrichissement des Données

**Ajout des Prix :**
- **Méthode** : Algorithmes de pricing basés sur la destination et la saison
- **Sources** : Données de marché, tendances saisonnières, coûts de vie locaux
- **Gamme de Prix** : Budget, moyen, luxe pour chaque destination
- **Facteurs** : Saisonnalité, popularité, type d'hébergement

**Mise à Jour de la Plage de Données :**
- **Destinations** : Focus sur l'Asie avec données enrichies
- **Informations** : Descriptions détaillées, conseils pratiques, informations culturelles
- **Métadonnées** : Tags, catégories, popularité, difficulté d'accès
- **Conseils** : Meilleure période, budget recommandé, activités populaires

### Structure des Données Vectorisées

**Composants des Données :**
- **Informations de Destination** : Nom, pays, région, description
- **Gamme de Prix** : Budget, moyen, luxe avec justifications
- **Description Détaillée** : Attractions, culture, gastronomie
- **Tags et Catégories** : Type de voyage, activités, public cible
- **Embeddings Vectoriels** : Représentation sémantique pour la recherche

**Index FAISS :**
- **Base Vectorielle** : Stockage des embeddings optimisé
- **Métadonnées** : Informations structurées pour le filtrage
- **Recherche de Similarité** : Algorithme de correspondance rapide

## Structure des Dossiers

### Dossier Principal (`/`)
```
cftravel/
├── src/                    # Code source Symfony
├── templates/              # Templates Twig
├── public/                 # Assets publics
├── assets/                 # Assets source
├── config/                 # Configuration Symfony
├── cftravel_py/           # Backend Python
├── scripts/               # Scripts de web scraping
├── vendor/                # Dépendances PHP
├── node_modules/          # Dépendances JavaScript
└── var/                   # Cache et logs Symfony
```

### Backend Python (`/cftravel_py/`)
```
cftravel_py/
├── api/                   # API FastAPI
│   ├── server.py         # Serveur principal
│   ├── semantic_api.py   # API sémantique
│   └── settings_api.py   # API de configuration
├── pipelines/            # Pipelines IA
│   ├── enhanced_modular_pipeline.py
│   ├── modular_pipeline.py
│   └── components/       # Composants IA
├── services/             # Services métier
├── models/               # Modèles de données
├── core/                 # Configuration et exceptions
└── data/                 # Données et index vectoriels
```

### Scripts de Scraping (`/scripts/`)
```
scripts/
├── scrape_asia_enhanced_auto.py  # Scraping automatique Asie
├── merge_enhanced_data.py        # Fusion des données
└── data_processor.py             # Traitement des données
```

## Composants Principaux

### 1. Contrôleurs Symfony (`/src/Controller/`)

**ChatController.php**
- Gestion des conversations utilisateur
- Routes principales : `/`, `/asia`, `/home`
- Intégration avec l'API Python
- Gestion CORS et sécurité

**DashboardController.php**
- Interface d'administration
- Gestion des modèles de sauvegarde

**DashboardApiController.php**
- API REST pour le dashboard
- Gestion des configurations

### 2. Services Symfony (`/src/Service/`)

**ApiService.php**
- Communication avec l'API Python
- Gestion des requêtes HTTP
- Gestion des erreurs et timeouts

**ConfigurationService.php**
- Gestion de la configuration unifiée
- Paramètres CORS
- Configuration des serveurs

### 3. Entités et Repository (`/src/Entity/`, `/src/Repository/`)

**Note :** Le projet n'utilise pas de base de données pour stocker les conversations. Les conversations sont gérées en mémoire et ne sont pas persistées.

### 4. API Python (`/cftravel_py/api/`)

**server.py**
- Serveur FastAPI principal
- Endpoints REST pour l'IA
- Gestion des streams de réponse
- Middleware CORS

**semantic_api.py**
- API pour la recherche sémantique
- Index vectoriel FAISS
- Recherche d'offres similaires

**settings_api.py**
- API de configuration
- Gestion des paramètres système

### 5. Pipelines IA (`/cftravel_py/pipelines/`)

**EnhancedASIAModularPipeline**
- Pipeline principal pour l'agent Asia.fr
- Composants intelligents :
  - Extracteur de préférences
  - Moteur de recommandation
  - Générateur de réponses
  - Orchestrateur de voyage

**Composants IA**
- `TravelOrchestrator` : Orchestration intelligente
- `EnhancedPreferenceExtractor` : Extraction des préférences
- `EnhancedRecommendationEngine` : Moteur de recommandation
- `ResponseGenerator` : Génération de réponses

### 6. Services Python (`/cftravel_py/services/`)

**LLMService**
- Interface avec Groq API
- Gestion des tokens et coûts
- Fallback vers modèles de sauvegarde
- Configuration des modèles GPT-OSS-120B et Kimi K2

**DataService**
- Gestion des données de voyage
- Chargement des offres
- Indexation vectorielle
- Accès aux données enrichies

**MemoryService**
- Gestion de la mémoire conversationnelle
- Stockage des contextes utilisateur

**OptimizedSemanticService**
- Service de recherche sémantique optimisé
- Index FAISS pour la recherche rapide
- Algorithmes de similarité cosinus

## Templates et Interface Utilisateur

### Templates Principaux (`/templates/`)

**base.html.twig**
- Template de base avec navigation
- Intégration des assets
- Configuration responsive

**chat/index.html.twig**
- Interface de chat principale
- Intégration avec l'agent IA
- Gestion des conversations

**dashboard.html.twig**
- Interface d'administration
- Gestion des modèles
- Configuration système

**home.html.twig**
- Page d'accueil marketing
- Présentation des fonctionnalités

### Composants (`/templates/components/`)

**Chat Components**
- `message.html.twig` : Affichage des messages
- `confirmation.html.twig` : Confirmation d'actions
- `offer-details-modal.html.twig` : Détails des offres

**Dashboard Components**
- `backup-model-dashboard.html.twig` : Gestion des modèles

## Assets et Frontend

### JavaScript (`/public/assets/js/`)

**Modules Principaux**
- `app.js` : Application principale
- `modules/chat/chat-core.js` : Logique de chat
- `modules/dashboard/` : Gestion du dashboard
- `services/api.service.js` : Service API
- `services/chat.service.js` : Service de chat

**Configuration**
- `config/unified-config.js` : Configuration unifiée
- `core/utils.js` : Utilitaires

### Styles (`/public/assets/css/`)

**Feuilles de Style**
- `output.css` : Styles Tailwind compilés
- `glightbox.css` : Galerie d'images
- `prism.css` : Coloration syntaxique

## Configuration et Déploiement

### Configuration Symfony (`/config/`)

**packages/**
- `framework.yaml` : Configuration Symfony
- `security.yaml` : Configuration sécurité
- `twig.yaml` : Configuration templates

### Configuration Python (`/cftravel_py/core/`)

**unified_config.py**
- Configuration unifiée pour tous les services
- Paramètres CORS
- Configuration des serveurs
- Configuration des modèles Groq

### Configuration des Modèles IA

**Fichier : `cftravel_py/core/unified_config.py`**
```python
LLM_CONFIG = {
    'groq_api_key': os.getenv('GROQ_API_KEY'),
    'model_name': 'gpt-oss-120b',
    'max_tokens': 1000,
    'temperature': 0.7,
    'fallback_model': 'kimi-k2',
    'backup_model': 'llama3-8b-8192'
}
```

## Logique IA et Algorithmes

### Pipeline de Traitement

1. **Réception de la requête utilisateur**
2. **Extraction des préférences** via LLM (GPT-OSS-120B)
3. **Recherche sémantique** dans la base d'offres enrichie
4. **Génération de recommandations** personnalisées
5. **Orchestration intelligente** des réponses
6. **Génération de réponse** contextuelle

### Composants IA Spécialisés

**Extracteur de Préférences**
- Analyse du langage naturel avec GPT-OSS-120B
- Identification des critères de voyage
- Extraction des contraintes budgétaires
- Compréhension des préférences culturelles

**Moteur de Recommandation**
- Recherche vectorielle FAISS
- Algorithme de similarité cosinus
- Filtrage intelligent des résultats
- Intégration des données enrichies (prix, conseils)

**Orchestrateur de Voyage**
- Coordination entre composants
- Gestion du contexte conversationnel
- Optimisation des réponses
- Adaptation aux préférences utilisateur
- Utilisation de Kimi K2 pour les analyses complexes

## Gestion des Données

### Stockage des Conversations

**Note :** Les conversations ne sont pas persistées en base de données. Elles sont gérées en mémoire pendant la session utilisateur et ne sont pas sauvegardées.

### Index Vectoriel

**FAISS Index**
- Embeddings des offres de voyage enrichies
- Recherche sémantique rapide
- Métadonnées optimisées
- Données mises à jour via web scraping

## Sécurité et Performance

### Sécurité
- Configuration CORS stricte
- Validation des entrées utilisateur
- Gestion sécurisée des API keys Groq
- Protection CSRF

### Performance
- Lazy loading des services Python
- Cache des index vectoriels
- Optimisation des requêtes
- Compression des assets
- Réponses ultra-rapides avec Groq LPU

## Points d'API

### Endpoints Principaux

**Chat API**
- `POST /chat` : Envoi de message
- `GET /conversations` : Récupération conversations
- `POST /stream` : Stream de réponses

**Settings API**
- `GET /settings` : Configuration système
- `PUT /settings` : Mise à jour configuration

**Semantic API**
- `POST /semantic/search` : Recherche sémantique
- `GET /offers` : Récupération offres

## Utilisation et Démarrage

### Prérequis
- PHP 8.1+
- Python 3.8+
- Node.js 16+

### Installation
1. Cloner le repository
2. Installer les dépendances PHP : `composer install`
3. Installer les dépendances Python : `pip install -r requirements.txt`
4. Installer les dépendances Node : `npm install`
5. Lancer les services

### Démarrage
1. API Python : `python -m cftravel_py.api.server`
2. Symfony : `symfony server:start -d`

## Fonctionnalités Actives

### Agent Asia.fr (Spécialisé)
- Focus sur les destinations asiatiques
- Données enrichies pour l'Asie (web scraping)
- Recommandations spécialisées avec prix
- Connaissance approfondie de la région

### Dashboard Administratif
- Gestion des modèles de sauvegarde
- Configuration système
- Monitoring des performances

### Interface de Chat
- Conversations en temps réel
- Affichage des offres détaillées
- Gestion en mémoire (non persistée)

## Maintenance et Évolution

### Logs et Monitoring
- Logs Symfony dans `/var/log/`
- Logs Python via logging standard
- Monitoring des performances API

### Sauvegarde
- Modèles de sauvegarde pour l'IA
- Index vectoriels FAISS
- Configuration système
- Données enrichies (web scraping)

### Évolutions Futures
- Amélioration des algorithmes IA
- Extension des données de voyage
- Optimisation des performances
- Mise à jour automatique des données via scraping 