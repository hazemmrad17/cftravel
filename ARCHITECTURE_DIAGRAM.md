# Diagramme d'Architecture - CFTravel

## Architecture Globale

```mermaid
graph TB
    subgraph "CFTravel Application"
        subgraph "Frontend Layer"
            UI[Interface Utilisateur<br/>Port 8001]
            TEMPLATES[Templates Twig]
            ASSETS[Assets JS/CSS]
        end
        
        subgraph "Symfony Backend"
            CONTROLLERS[Contrôleurs]
            SERVICES[Services]
            CONFIG[Configuration]
        end
        
        subgraph "Python AI Backend"
            FASTAPI[FastAPI Server<br/>Port 8000]
            PIPELINES[Pipelines IA]
            AI_SERVICES[Services IA]
        end
        
        subgraph "Data Layer"
            VECTOR_DB[Index Vectoriel FAISS]
            AI_MODELS[Modèles Groq]
        end
    end
    
    UI --> CONTROLLERS
    CONTROLLERS --> SERVICES
    SERVICES --> FASTAPI
    FASTAPI --> PIPELINES
    PIPELINES --> AI_SERVICES
    AI_SERVICES --> VECTOR_DB
    AI_SERVICES --> AI_MODELS
    
    TEMPLATES --> UI
    ASSETS --> UI
    CONFIG --> SERVICES
```

## Flux de Données

### 1. Flux de Chat Utilisateur

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant S as Symfony
    participant P as Python API
    participant AI as Pipeline IA
    
    U->>F: Message utilisateur
    F->>S: Requête HTTP
    S->>P: Appel API Python
    P->>AI: Traitement IA
    AI->>P: Réponse IA
    P->>S: Réponse API
    S->>F: Réponse HTTP
    F->>U: Affichage réponse
```

### 2. Flux de Recherche Sémantique

```mermaid
flowchart LR
    A[Requête Utilisateur] --> B[Semantic API]
    B --> C[FAISS Index]
    C --> D[Vector Search]
    D --> E[Similarity Algorithm]
    E --> F[Filtered Results]
    F --> G[Response Generation]
```

## Architecture des Composants

### Backend Symfony

```mermaid
graph TB
    subgraph "Symfony Application"
        subgraph "Controllers"
            CHAT[ChatController]
            DASH[DashboardController]
            API[DashboardApiController]
        end
        
        subgraph "Services"
            API_SERVICE[ApiService]
            CONFIG_SERVICE[ConfigurationService]
        end
        
        subgraph "Templates"
            TWIG[Templates Twig]
            COMPONENTS[Components]
        end
        
        subgraph "Assets"
            JS[JavaScript]
            CSS[Styles]
        end
    end
    
    CHAT --> API_SERVICE
    DASH --> CONFIG_SERVICE
    API --> API_SERVICE
    
    TWIG --> CHAT
    COMPONENTS --> CHAT
    JS --> CHAT
    CSS --> CHAT
```

### Backend Python IA

```mermaid
graph TB
    subgraph "Python AI Backend"
        subgraph "API Layer"
            SERVER[FastAPI Server]
            SEMANTIC[Semantic API]
            SETTINGS[Settings API]
        end
        
        subgraph "Pipeline Layer"
            ENHANCED[Enhanced Pipeline]
            MODULAR[Modular Pipeline]
            COMPONENTS[IA Components]
        end
        
        subgraph "Services Layer"
            LLM[LLM Service]
            DATA[Data Service]
            MEMORY[Memory Service]
            SEMANTIC_SVC[Semantic Service]
        end
        
        subgraph "Data Layer"
            FAISS[FAISS Index]
            EMBEDDINGS[Embeddings]
            OFFERS[Travel Offers]
        end
    end
    
    SERVER --> ENHANCED
    SEMANTIC --> SEMANTIC_SVC
    SETTINGS --> LLM
    
    ENHANCED --> COMPONENTS
    COMPONENTS --> LLM
    COMPONENTS --> DATA
    COMPONENTS --> MEMORY
    
    DATA --> FAISS
    SEMANTIC_SVC --> EMBEDDINGS
    DATA --> OFFERS
```

## Pipeline IA Détaillé

```mermaid
graph TB
    subgraph "Enhanced ASIA Modular Pipeline"
        subgraph "Input Processing"
            MSG[Message Parsing]
            CTX[Context Analysis]
            PREF[Preferences Extraction]
        end
        
        subgraph "Orchestration"
            ORCH[Travel Orchestrator]
            INTENT[Intent Detection]
            STRATEGY[Strategy Selection]
        end
        
        subgraph "AI Components"
            PREF_EX[Preference Extractor]
            REC_ENG[Recommendation Engine]
            RESP_GEN[Response Generator]
        end
        
        subgraph "AI Services"
            GROQ[Groq LLM]
            FAISS_SEARCH[FAISS Search]
            MEMORY_SVC[Memory Service]
        end
        
        subgraph "Output"
            CONTEXT[Context Building]
            FORMAT[Response Formatting]
            VALIDATION[Quality Validation]
        end
    end
    
    MSG --> ORCH
    CTX --> ORCH
    PREF --> ORCH
    
    ORCH --> INTENT
    ORCH --> STRATEGY
    
    INTENT --> PREF_EX
    STRATEGY --> REC_ENG
    REC_ENG --> RESP_GEN
    
    PREF_EX --> GROQ
    REC_ENG --> FAISS_SEARCH
    RESP_GEN --> MEMORY_SVC
    
    GROQ --> CONTEXT
    FAISS_SEARCH --> FORMAT
    MEMORY_SVC --> VALIDATION
```

## Architecture Frontend

```mermaid
graph TB
    subgraph "Frontend Architecture"
        subgraph "Templates Layer"
            BASE[Base Templates]
            CHAT[Chat Interface]
            DASH[Dashboard Interface]
        end
        
        subgraph "JavaScript Layer"
            CORE[Core Utils]
            CHAT_JS[Chat Module]
            DASH_JS[Dashboard Module]
        end
        
        subgraph "Services Layer"
            API_SVC[API Service]
            CHAT_SVC[Chat Service]
            STORAGE[Storage Service]
        end
        
        subgraph "UI Framework"
            ALPINE[Alpine.js]
            LUCIDE[Lucide Icons]
            TAILWIND[Tailwind CSS]
        end
    end
    
    BASE --> CHAT
    BASE --> DASH
    
    CHAT --> CHAT_JS
    DASH --> DASH_JS
    
    CHAT_JS --> CHAT_SVC
    DASH_JS --> API_SVC
    
    CHAT_SVC --> STORAGE
    API_SVC --> STORAGE
    
    ALPINE --> CHAT_JS
    LUCIDE --> CHAT_JS
    TAILWIND --> CHAT_JS
```

## Points d'Intégration

### Communication Symfony ↔ Python

```mermaid
sequenceDiagram
    participant S as Symfony
    participant AS as ApiService
    participant P as Python API
    participant AI as AI Pipeline
    
    S->>AS: HTTP Request
    AS->>P: API Call
    P->>AI: Process Request
    AI->>P: AI Response
    P->>AS: API Response
    AS->>S: HTTP Response
```

### Flux de Données Vectorielles

```mermaid
flowchart LR
    A[User Query] --> B[Semantic API]
    B --> C[FAISS Index]
    C --> D[Vector Search]
    D --> E[Similarity Algorithm]
    E --> F[Results Filtering]
    F --> G[Response]
```

## Sécurité et Performance

### Architecture de Sécurité

```mermaid
graph TB
    subgraph "Security Layer"
        subgraph "CORS"
            ORIGINS[Allowed Origins]
            METHODS[Allowed Methods]
            HEADERS[Allowed Headers]
        end
        
        subgraph "Validation"
            INPUT[Input Validation]
            SANITIZE[Data Sanitization]
            ESCAPE[Output Escaping]
        end
        
        subgraph "API Security"
            API_KEYS[API Key Management]
            RATE_LIMIT[Rate Limiting]
            TOKEN_TRACK[Token Tracking]
        end
    end
    
    ORIGINS --> INPUT
    METHODS --> SANITIZE
    HEADERS --> ESCAPE
    
    INPUT --> API_KEYS
    SANITIZE --> RATE_LIMIT
    ESCAPE --> TOKEN_TRACK
```

### Optimisations de Performance

```mermaid
graph TB
    subgraph "Performance Optimizations"
        subgraph "Lazy Loading"
            SERVICES[Services Loading]
            PIPELINE[Pipeline Loading]
            TEMPLATES[Template Loading]
        end
        
        subgraph "Caching"
            VECTOR[Vector Index Cache]
            RESPONSE[Response Cache]
            ASSETS[Asset Cache]
        end
        
        subgraph "Asset Optimization"
            WEBPACK[Webpack Encore]
            COMPRESSION[Asset Compression]
            MINIFICATION[Code Minification]
        end
    end
    
    SERVICES --> VECTOR
    PIPELINE --> RESPONSE
    TEMPLATES --> ASSETS
    
    VECTOR --> WEBPACK
    RESPONSE --> COMPRESSION
    ASSETS --> MINIFICATION
```

## Modèles IA et Capacités

### Modèles Groq Utilisés

```mermaid
graph TB
    subgraph "Groq Models"
        GPT_OSS[GPT-OSS-120B<br/>120B Parameters]
        KIMI_K2[Kimi K2<br/>1T Parameters]
        LLAMA3[Llama 3 8B<br/>Fallback Only]
    end
    
    subgraph "Model Capabilities"
        SPEED[Vitesse Ultra-rapide<br/>Réponses en ms]
        LATENCY[Latence Ultra-faible<br/>LPU Technology]
        QUALITY[Qualité Exceptionnelle<br/>Open Source Models]
        COST[Coût Optimisé<br/>Tarification compétitive]
        GIANT[Modèles Géants<br/>1T Parameters Support]
    end
    
    GPT_OSS --> SPEED
    KIMI_K2 --> LATENCY
    GPT_OSS --> QUALITY
    KIMI_K2 --> GIANT
    LLAMA3 --> COST
```

### Choix des Modèles

**GPT-OSS-120B (Modèle Principal)**
- **Capacités** : Modèle open source de 120 milliards de paramètres
- **Contexte** : Large contexte pour les conversations complexes
- **Vitesse** : Réponses ultra-rapides grâce aux LPU de Groq
- **Avantages** : Modèle open source récemment libéré, performances élevées

**Kimi K2 (Modèle Secondaire - 1T Paramètres)**
- **Capacités** : Modèle de 1 trillion de paramètres (1T)
- **Contexte** : Contexte extrêmement large pour l'analyse approfondie
- **Utilisation** : Traitement des requêtes complexes nécessitant une compréhension profonde
- **Avantages** : Modèle le plus puissant disponible, récemment open source
- **Particularité** : Premier modèle de 1T paramètres accessible via API

**Llama 3 8B (Modèle de Fallback)**
- **Capacités** : Modèle léger et rapide
- **Utilisation** : Fallback en cas de problème avec les modèles principaux
- **Avantages** : Fiabilité et stabilité éprouvées

### Avantages de Groq

- **LPU Technology** : Processeurs spécialisés pour le langage
- **Latence Ultra-faible** : Idéal pour les applications interactives
- **Scalabilité** : Infrastructure capable de gérer les modèles de 1T paramètres
- **Modèles Open Source Récents** : GPT-OSS-120B et Kimi K2
- **Support Modèles Géants** : Capacité unique d'exécuter des modèles de 1T paramètres

## Web Scraping et Base de Données

### Processus de Collecte de Données

```mermaid
flowchart LR
    A[Web Scraping Scripts] --> B[Data Extraction]
    B --> C[Price Addition]
    C --> D[Data Enrichment]
    D --> E[Vector Indexing]
    E --> F[FAISS Database]
```

### Scripts de Web Scraping

**Scripts Utilisés :**
- `scripts/scrape_asia_enhanced_auto.py` : Scraping automatique des destinations asiatiques
- `scripts/merge_enhanced_data.py` : Fusion et enrichissement des données

**Technologies de Scraping :**
- **BeautifulSoup4** : Parsing HTML et extraction de contenu
- **Requests** : Requêtes HTTP pour récupérer les pages
- **Pandas** : Traitement et manipulation des données
- **NumPy** : Calculs numériques pour les prix

### Enrichissement des Données

**Ajout des Prix :**
- **Méthode** : Algorithmes de pricing basés sur la destination et la saison
- **Sources** : Données de marché, tendances saisonnières
- **Gamme de Prix** : Budget, moyen, luxe pour chaque destination

**Mise à Jour de la Plage de Données :**
- **Destinations** : Focus sur l'Asie avec données enrichies
- **Informations** : Descriptions détaillées, conseils pratiques
- **Métadonnées** : Tags, catégories, popularité

### Structure des Données Vectorisées

```mermaid
graph TB
    subgraph "Data Structure"
        DESTINATION[Destination Info]
        PRICE_RANGE[Price Range]
        DESCRIPTION[Detailed Description]
        TAGS[Tags & Categories]
        EMBEDDINGS[Vector Embeddings]
    end
    
    subgraph "FAISS Index"
        VECTOR_DB[Vector Database]
        METADATA[Metadata Storage]
        SIMILARITY[Similarity Search]
    end
    
    DESTINATION --> EMBEDDINGS
    PRICE_RANGE --> EMBEDDINGS
    DESCRIPTION --> EMBEDDINGS
    TAGS --> EMBEDDINGS
    
    EMBEDDINGS --> VECTOR_DB
    EMBEDDINGS --> METADATA
    VECTOR_DB --> SIMILARITY
```

### Avantages de l'Approche

**Données Enrichies :**
- Informations complètes sur chaque destination
- Prix réalistes et à jour
- Conseils pratiques et culturels

**Recherche Sémantique Avancée :**
- Compréhension des préférences utilisateur
- Recommandations personnalisées
- Correspondance intelligente des offres

**Performance Optimisée :**
- Index vectoriel FAISS pour recherche rapide
- Métadonnées structurées pour filtrage
- Mise à jour automatique des données 