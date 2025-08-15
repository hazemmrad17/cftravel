# CFTravel - Agent IA de Voyage

## Vue d'ensemble

CFTravel est une application web hybride qui combine une interface utilisateur moderne (Symfony/PHP) avec un backend d'intelligence artificielle Python pour fournir des recommandations de voyage personnalisées.

Le projet propose un agent IA spécialisé :
- **Asia.fr** : Agent spécialisé pour les destinations asiatiques

## Fonctionnalités Principales

### Agents IA Intelligents
- Analyse du langage naturel pour comprendre les préférences
- Recherche sémantique dans une base d'offres vectorisée
- Recommandations personnalisées basées sur le contexte
- Gestion de la mémoire conversationnelle

### Interface Utilisateur Moderne
- Interface de chat en temps réel
- Dashboard d'administration
- Design responsive avec Tailwind CSS
- Composants interactifs avec Alpine.js

### Architecture Technique
- Backend Symfony (PHP) pour l'interface utilisateur
- API Python (FastAPI) pour l'intelligence artificielle
- Gestion en mémoire pour les conversations (non persistées)
- Index vectoriel FAISS pour la recherche sémantique

## Documentation

### 📚 Documentation Complète
- **[Documentation Technique](DOCUMENTATION.md)** - Architecture détaillée et composants
- **[Diagrammes d'Architecture](ARCHITECTURE_DIAGRAM.md)** - Schémas et flux de données
- **[Guide d'Installation](GUIDE_INSTALLATION.md)** - Installation et configuration

### 🚀 Démarrage Rapide

**Prérequis**
- PHP 8.1+
- Python 3.8+
- Node.js 16+

**Installation**
```bash
# Cloner le projet
git clone <repository-url>
cd cftravel

# Configuration
cp env.example .env
# Éditer .env avec vos paramètres

# Installation des dépendances
composer install
pip install -r requirements.txt
npm install

# Compilation des assets
npm run build
```

**Démarrage**
```bash
# API Python (Terminal 1)
cd cftravel_py
python -m api.server

# Symfony (Terminal 2)
symfony server:start -d
```

**Accès**
- Application : http://localhost:8001
- API Python : http://localhost:8000
- Dashboard : http://localhost:8001/dashboard

## Structure du Projet

```
cftravel/
├── src/                    # Code source Symfony
│   ├── Controller/        # Contrôleurs web
│   ├── Service/          # Services métier
│   ├── Entity/           # Modèles de données
│   └── Repository/       # Accès aux données
├── templates/             # Templates Twig
├── public/               # Assets publics
├── assets/               # Assets source
├── cftravel_py/         # Backend Python IA
│   ├── api/             # API FastAPI
│   ├── pipelines/       # Pipelines IA
│   ├── services/        # Services métier
│   └── data/            # Données et index
├── config/              # Configuration Symfony
└── var/                 # Cache et logs
```

## Technologies Utilisées

### Backend Frontend
- **Symfony 6.4** - Framework PHP
- **Twig** - Moteur de templates
- **Webpack Encore** - Gestion des assets

### Backend IA
- **FastAPI** - Framework API Python
- **Groq** - API LLM haute performance
- **LangChain** - Framework IA
- **FAISS** - Index vectoriel
- **Sentence Transformers** - Embeddings

### Frontend
- **Alpine.js** - Framework JavaScript léger
- **Tailwind CSS** - Framework CSS utilitaire
- **Lucide Icons** - Icônes modernes
- **Stimulus** - Contrôleurs JavaScript

### Gestion des Données
- **Mémoire** - Conversations en session
- **FAISS** - Index vectoriel pour la recherche

## À propos de Groq

**Groq** est une API de modèles de langage (LLM) qui se distingue par sa vitesse exceptionnelle et sa latence ultra-faible. Contrairement aux autres fournisseurs LLM, Groq utilise des processeurs spécialisés (LPU - Language Processing Units) qui permettent des réponses en temps réel, même pour des modèles complexes comme GPT-OSS-120B (120B paramètres) et Kimi K2 (1T paramètres).

**Avantages de Groq :**
- **Vitesse** : Réponses en millisecondes
- **Latence faible** : Idéal pour les applications interactives
- **Modèles géants** : Support de modèles de 1 trillion de paramètres
- **Modèles open source** : GPT-OSS-120B et Kimi K2 récemment libérés
- **Coût optimisé** : Tarification compétitive
- **Fiabilité** : Infrastructure robuste et stable

## Fonctionnalités Détaillées

### Agent Asia.fr (Spécialisé)
- Focus sur les destinations asiatiques
- Données enrichies pour l'Asie
- Recommandations spécialisées
- Connaissance approfondie de la région

### Interface de Chat
- Conversations en temps réel
- Affichage des offres détaillées
- Gestion en mémoire (non persistée)
- Interface intuitive et responsive

### Dashboard Administratif
- Gestion des modèles de sauvegarde
- Configuration système
- Monitoring des performances
- Gestion des utilisateurs

## API Endpoints

### Chat API
- `POST /chat` - Envoi de message
- `GET /conversations` - Récupération conversations
- `POST /stream` - Stream de réponses

### Settings API
- `GET /settings` - Configuration système
- `PUT /settings` - Mise à jour configuration

### Semantic API
- `POST /semantic/search` - Recherche sémantique
- `GET /offers` - Récupération offres

## Configuration

### Variables d'Environnement
```bash
# Symfony
APP_ENV=dev
APP_SECRET=votre_secret

# API Python
BACKEND_URL=http://localhost:8000
GROQ_API_KEY=votre_clé_groq
```

### Ports Utilisés
- **8000** : API Python (FastAPI)
- **8001** : Application Symfony

## Développement

### Scripts Utiles
```bash
# Démarrage complet
./start.sh

# Arrêt des services
./stop.sh

# Tests
php bin/phpunit
python -m pytest cftravel_py/tests/

# Linting
composer cs-fix
npm run lint
```

### Structure des Tests
- **PHP** : Tests unitaires Symfony
- **Python** : Tests des pipelines IA
- **Frontend** : Tests d'intégration

## Déploiement

### Production
- Configuration des variables d'environnement
- Optimisation des assets
- Configuration du serveur web
- Mise en place du monitoring

## Maintenance

### Logs
- Logs Symfony : `var/log/`
- Logs Python : `cftravel_py/logs/`

### Sauvegarde
- Index vectoriels FAISS
- Configuration système
- Modèles de sauvegarde IA

### Mise à Jour
- Dépendances PHP via Composer
- Dépendances Python via pip
- Dépendances Node via npm

## Support

### Documentation
- Documentation technique complète
- Guides d'installation
- Diagrammes d'architecture

### Dépannage
- Logs d'erreur détaillés
- Tests de connectivité
- Scripts de diagnostic

### Contact
Pour toute question ou problème :
- Consulter la documentation
- Vérifier les logs
- Tester les services individuellement

## Licence

Ce projet est développé dans le cadre d'un stage/internship. Tous droits réservés.

## Équipe

- **Développeur Principal** : [Votre Nom]
- **Superviseur** : [Nom du Superviseur]
- **Institution** : [Nom de l'Institution]

---

*CFTravel - Révolutionner les recommandations de voyage avec l'intelligence artificielle* 