# ASIA.fr Travel Agent

A hybrid PHP/Symfony + Python/FastAPI travel chat application with AI-powered travel recommendations.

## 🚀 Features

- **AI-Powered Chat**: Real-time conversation with ASIA.fr Agent using Groq LLM
- **Travel Recommendations**: Intelligent offer matching based on user preferences
- **Streaming Responses**: Real-time character-by-character response streaming
- **Hybrid Architecture**: Symfony frontend with Python AI backend
- **Modern UI**: Responsive chat interface with offer cards

## 🏗️ Architecture

```
├── public/                 # Symfony public assets
│   └── assets/js/         # Frontend JavaScript
├── src/                   # Symfony PHP code
│   └── Controller/        # PHP controllers
├── cftravel_py/          # Python AI backend
│   ├── api/              # FastAPI server
│   ├── core/             # Configuration and constants
│   ├── models/           # Data models
│   ├── pipelines/        # AI processing pipelines
│   ├── services/         # Business logic services
│   └── data/             # Travel data
└── templates/            # Symfony templates
```

## 🛠️ Technology Stack

### Frontend
- **Symfony 6**: PHP framework
- **JavaScript**: Vanilla JS with modern ES6+ features
- **CSS**: Modern styling with responsive design

### Backend
- **Python 3.11+**: Core AI logic
- **FastAPI**: High-performance API framework
- **Groq**: LLM provider for AI responses
- **Sentence Transformers**: Text embeddings

## 📋 Prerequisites

- PHP 8.1+
- Python 3.11+
- Composer
- Node.js (for asset compilation)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd cftravel3
```

### 2. Install Dependencies

#### PHP/Symfony
```bash
composer install
```

#### Python
```bash
cd cftravel_py
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory:
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Model Configuration
REASONING_MODEL=openai/gpt-oss-120b
GENERATION_MODEL=llama-3.1-8b-instant
MATCHER_MODEL=llama-3.1-8b-instant
EXTRACTOR_MODEL=llama-3.1-8b-instant

# API Configuration
AGENT_API_URL=http://localhost:8001
```

### 4. Start the Servers

#### Start Python AI Backend (Port 8001)
```bash
python -m uvicorn cftravel_py.api.server:app --host 0.0.0.0 --port 8001
```

#### Start Symfony Frontend (Port 8000)
```bash
# Option 1: Symfony CLI
symfony server:start -d --port=8000

# Option 2: PHP built-in server
php -S localhost:8000 -t public
```

### 5. Access the Application

Open your browser and go to: **http://localhost:8000**

## 🎯 Usage

1. **Start a Conversation**: Type your travel preferences
2. **Get AI Recommendations**: Receive personalized travel offers
3. **Explore Offers**: View detailed travel packages with pricing
4. **Manage Preferences**: Update your travel preferences anytime

## 🔧 Configuration

### AI Models
The application uses multiple AI models for different tasks:
- **Orchestrator**: Makes conversation decisions
- **Generator**: Creates natural responses
- **Matcher**: Matches offers to preferences
- **Extractor**: Extracts user preferences

### Environment Variables

#### Required
- `GROQ_API_KEY`: Your Groq API key

#### Model Configuration (Optional - uses defaults if not set)
- `REASONING_MODEL`: Model for orchestration (default: openai/gpt-oss-120b)
- `GENERATION_MODEL`: Model for response generation (default: llama-3.1-8b-instant)
- `MATCHER_MODEL`: Model for offer matching (default: llama-3.1-8b-instant)
- `EXTRACTOR_MODEL`: Model for preference extraction (default: llama-3.1-8b-instant)
- `EMBEDDING_MODEL`: Embedding model for semantic search (default: all-MiniLM-L6-v2)

#### Model Parameters (Optional - uses defaults if not set)
- `REASONING_TEMPERATURE`: Temperature for reasoning model (default: 0.1)
- `GENERATION_TEMPERATURE`: Temperature for generation model (default: 0.7)
- `MATCHER_TEMPERATURE`: Temperature for matching model (default: 0.3)
- `EXTRACTOR_TEMPERATURE`: Temperature for extraction model (default: 0.1)
- `REASONING_MAX_TOKENS`: Max tokens for reasoning model (default: 2048)
- `GENERATION_MAX_TOKENS`: Max tokens for generation model (default: 2048)
- `MATCHER_MAX_TOKENS`: Max tokens for matching model (default: 2048)
- `EXTRACTOR_MAX_TOKENS`: Max tokens for extraction model (default: 1024)

#### API Configuration (Optional - uses defaults if not set)
- `GROQ_BASE_URL`: Groq API base URL (default: https://api.groq.com/openai/v1)
- `AGENT_API_URL`: Internal API URL (default: http://localhost:8001)

#### Other Settings (Optional)
- `DEBUG`: Enable debug mode (default: false)
- `DATA_PATH`: Path to travel data (default: ./cftravel_py/data)

## 📁 Project Structure

```
cftravel3/
├── public/                 # Web assets
│   └── assets/
│       └── js/
│           └── chat.js     # Main chat interface
├── src/
│   └── Controller/
│       └── ChatController.php  # PHP API endpoints
├── cftravel_py/
│   ├── api/
│   │   └── server.py       # FastAPI server
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   └── constants.py    # Constants
│   ├── models/
│   │   ├── data_models.py  # Request/response models
│   │   └── response_models.py
│   ├── pipelines/
│   │   └── concrete_pipeline.py  # AI processing
│   ├── services/
│   │   ├── data_service.py
│   │   ├── llm_service.py
│   │   ├── memory_service.py
│   │   └── offer_service.py
│   └── data/
│       └── travel_offers/  # Travel data
├── templates/              # Symfony templates
├── composer.json           # PHP dependencies
├── package.json            # Node.js dependencies
└── README.md              # This file
```

## 🔌 API Endpoints

### Python Backend (Port 8001)
- `GET /health` - Health check
- `POST /chat` - Send message
- `POST /chat/stream` - Streaming chat
- `GET /status` - Agent status
- `GET /welcome` - Welcome message
- `POST /memory/clear` - Clear conversation memory
- `GET /preferences` - Get user preferences
- `POST /preferences` - Update preferences
- `DELETE /preferences` - Clear preferences

### Symfony Frontend (Port 8000)
- `GET /` - Main chat interface
- `POST /chat/message` - Forward to Python API
- `POST /chat/stream` - Forward streaming
- `POST /chat/memory/clear` - Forward memory clear

## 🧪 Testing

### Test Python API
```bash
cd cftravel_py
python -m pytest tests/
```

### Test Frontend
```bash
# Open browser and test chat functionality
# Send test messages and verify responses
```

## 🚀 Deployment

### Production Setup
1. Set up proper environment variables
2. Configure web server (Nginx/Apache)
3. Set up SSL certificates
4. Configure database if needed
5. Set up monitoring and logging

### Docker (Optional)
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🔄 Version History

- **v1.0.0**: Initial release with AI-powered travel chat
- **v1.1.0**: Added streaming responses and offer matching
- **v1.2.0**: Enhanced UI and preference management

---

**Made with ❤️ for ASIA.fr** 