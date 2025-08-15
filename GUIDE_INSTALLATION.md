# Guide d'Installation et Configuration - CFTravel

## Prérequis Système

### Logiciels Requis

**PHP**
- Version : 8.1 ou supérieure
- Extensions : ctype, iconv
- Composer : Dernière version stable

**Python**
- Version : 3.8 ou supérieure
- pip : Dernière version stable
- virtualenv (recommandé)

**Node.js**
- Version : 16 ou supérieure
- npm : Dernière version stable

**Système**
- Git
- Make (optionnel)
- 4GB RAM minimum
- 2GB espace disque libre

## Installation Étape par Étape

### 1. Clonage du Repository

```bash
git clone <repository-url>
cd cftravel
```

### 2. Configuration de l'Environnement

**Copier le fichier d'environnement**
```bash
cp env.example .env
```

**Éditer le fichier .env**
```bash
# Configuration Symfony
APP_ENV=dev
APP_SECRET=votre_secret_ici

# Configuration API Python
BACKEND_URL=http://localhost:8000

# Configuration Groq (optionnel)
GROQ_API_KEY=votre_clé_groq_ici
```

### 3. Installation des Dépendances PHP

```bash
# Installation via Composer
composer install

# Vérification des dépendances
composer check-platform-reqs
```

### 4. Installation des Dépendances Python

```bash
# Création d'un environnement virtuel (recommandé)
python -m venv venv

# Activation de l'environnement virtuel
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Vérification de l'installation
python -c "import fastapi, groq, numpy; print('Installation Python réussie')"
```

### 5. Installation des Dépendances Node.js

```bash
# Installation des packages
npm install

# Vérification de l'installation
npm run build
```

### 6. Configuration des Assets

```bash
# Compilation des assets
npm run build

# Ou pour le développement
npm run watch
```

### 7. Configuration des Permissions

```bash
# Création des dossiers de cache
mkdir -p var/cache var/log

# Attribution des permissions (Linux/Mac)
chmod -R 777 var/
chmod -R 777 public/uploads/ 2>/dev/null || mkdir -p public/uploads && chmod -R 777 public/uploads/
```

## Démarrage des Services

### 1. Démarrage de l'API Python

```bash
# Activation de l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Démarrage du serveur FastAPI
python -m cftravel_py.api.server

# Le serveur sera accessible sur http://localhost:8000
```

### 2. Démarrage de Symfony

```bash
# Démarrage du serveur Symfony
symfony server:start -d

# Ou avec PHP intégré
php -S localhost:8001 -t public/

# L'application sera accessible sur http://localhost:8001
```

### 3. Vérification des Services

**Test de l'API Python**
```bash
curl http://localhost:8000/health
# Réponse attendue : {"status": "healthy"}
```

**Test de Symfony**
```bash
curl http://localhost:8001/
# Réponse attendue : Page HTML de l'application
```

**Note :** Aucune base de données n'est requise pour le fonctionnement de base.

## Configuration Avancée

### Configuration CORS

**Fichier : `cftravel_py/core/unified_config.py`**
```python
CORS_CONFIG = {
    'allowed_origins': [
        'http://localhost:8001',
        'http://127.0.0.1:8001',
        # Ajouter vos domaines de production
    ],
    'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allowed_headers': ['*'],
    'allow_credentials': True
}
```

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

## Scripts d'Automatisation

### Script de Démarrage Complet

**Fichier : `start.sh` (Linux/Mac)**
```bash
#!/bin/bash

echo "🚀 Démarrage de CFTravel..."

# Vérification des prérequis
echo "📋 Vérification des prérequis..."
command -v php >/dev/null 2>&1 || { echo "❌ PHP non trouvé"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python non trouvé"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ Node.js non trouvé"; exit 1; }

# Compilation des assets
echo "🎨 Compilation des assets..."
npm run build

# Démarrage de l'API Python
echo "🐍 Démarrage de l'API Python..."
cd cftravel_py
source ../venv/bin/activate
python -m api.server &
PYTHON_PID=$!
cd ..

# Démarrage de Symfony
echo "⚡ Démarrage de Symfony..."
symfony server:start -d

echo "✅ CFTravel démarré avec succès!"
echo "🌐 Application : http://localhost:8001"
echo "🔌 API Python : http://localhost:8000"
echo ""
echo "Pour arrêter : ./stop.sh"
```

**Fichier : `stop.sh` (Linux/Mac)**
```bash
#!/bin/bash

echo "🛑 Arrêt de CFTravel..."

# Arrêt de Symfony
symfony server:stop

# Arrêt de l'API Python
pkill -f "python -m api.server"

echo "✅ CFTravel arrêté"
```

### Script Windows

**Fichier : `start.bat` (Windows)**
```batch
@echo off
echo 🚀 Démarrage de CFTravel...

REM Vérification des prérequis
echo 📋 Vérification des prérequis...
where php >nul 2>&1 || (echo ❌ PHP non trouvé && exit /b 1)
where python >nul 2>&1 || (echo ❌ Python non trouvé && exit /b 1)
where npm >nul 2>&1 || (echo ❌ Node.js non trouvé && exit /b 1)

REM Compilation des assets
echo 🎨 Compilation des assets...
npm run build

REM Démarrage de l'API Python
echo 🐍 Démarrage de l'API Python...
cd cftravel_py
call ..\venv\Scripts\activate
start "API Python" python -m api.server
cd ..

REM Démarrage de Symfony
echo ⚡ Démarrage de Symfony...
symfony server:start -d

echo ✅ CFTravel démarré avec succès!
echo 🌐 Application : http://localhost:8001
echo 🔌 API Python : http://localhost:8000
pause
```

## Tests et Validation

### Tests de Fonctionnalité

**Test de l'Interface de Chat**
1. Ouvrir http://localhost:8001
2. Taper un message de test
3. Vérifier la réponse de l'agent

**Test de l'Agent Asia.fr**
1. Ouvrir http://localhost:8001/asia
2. Demander une recommandation pour l'Asie
3. Vérifier la réponse spécialisée

**Test du Dashboard**
1. Ouvrir http://localhost:8001/dashboard
2. Vérifier l'affichage des configurations

### Tests API

**Test de l'API Python**
```bash
# Test de santé
curl http://localhost:8000/health

# Test de chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour", "agent": "asia"}'

# Test de recherche sémantique
curl -X POST http://localhost:8000/semantic/search \
  -H "Content-Type: application/json" \
  -d '{"query": "voyage en Asie"}'
```

### Tests de Performance

**Test de Charge Simple**
```bash
# Test avec Apache Bench
ab -n 100 -c 10 http://localhost:8001/

# Test de l'API
ab -n 50 -c 5 -p test_data.json -T application/json http://localhost:8000/chat
```

## Dépannage

### Problèmes Courants

**Erreur API Python**
```bash
# Vérifier les logs Python
tail -f cftravel_py/logs/app.log

# Vérifier les dépendances
pip list | grep fastapi

# Redémarrer l'API
pkill -f "python -m api.server"
python -m cftravel_py.api.server
```

**Erreur Assets Symfony**
```bash
# Nettoyer le cache
php bin/console cache:clear

# Recompiler les assets
npm run build

# Vérifier les permissions
chmod -R 777 var/
```

**Erreur CORS**
```bash
# Vérifier la configuration CORS
cat cftravel_py/core/unified_config.py | grep CORS

# Vérifier les headers de réponse
curl -I http://localhost:8000/health
```

### Logs et Monitoring

**Logs Symfony**
```bash
# Logs d'application
tail -f var/log/dev.log

# Logs d'erreur
tail -f var/log/error.log
```

**Logs Python**
```bash
# Logs de l'API
tail -f cftravel_py/logs/api.log

# Logs des pipelines
tail -f cftravel_py/logs/pipeline.log
```

**Monitoring des Services**
```bash
# Statut des processus
ps aux | grep -E "(symfony|python)"

# Utilisation des ports
netstat -tulpn | grep -E "(8000|8001)"

# Utilisation mémoire
free -h
```

## Maintenance

### Sauvegarde

**Sauvegarde des Index Vectoriels**
```bash
# Copie des fichiers FAISS
cp -r cftravel_py/data/vector_index/ backup_vector_index_$(date +%Y%m%d)/
```

### Mise à Jour

**Mise à Jour des Dépendances**
```bash
# PHP
composer update

# Python
pip install -r requirements.txt --upgrade

# Node.js
npm update
```

## Support et Contact

Pour toute question ou problème :
- Consulter les logs d'erreur
- Vérifier la configuration
- Tester les services individuellement
- Consulter la documentation technique 