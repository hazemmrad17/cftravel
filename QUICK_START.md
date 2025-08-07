# 🚀 Quick Start Guide - Layla Travel Agent Integration

## What We've Built

✅ **Python FastAPI Server** (`cftravel_py/api_server.py`)
- Exposes the travel agent as a REST API
- Handles chat messages, preferences, and status
- Runs on port 8000

✅ **Enhanced Symfony Controller** (`src/Controller/ChatController.php`)
- Communicates with the Python API
- Handles web requests and responses
- Provides error handling and logging

✅ **Improved Chat Interface** (`templates/chat/index.html.twig`)
- Modern chat UI with typing indicators
- Welcome message for travel agent
- Better error handling and user experience

✅ **Startup Scripts**
- `start_servers.sh` (Linux/Mac)
- `start_servers.bat` (Windows)
- `test_integration.py` (Verification script)

## 🎯 Next Steps

### 1. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Symfony Configuration
APP_ENV=dev
APP_SECRET=your-secret-key

# Travel Agent API
AGENT_API_URL=http://localhost:8000
```

### 2. Configure Python Agent

Create `cftravel_py/.env`:

```env
# Groq Configuration (if you have API key)
GROQ_API_KEY=your-groq-api-key
USE_GROQ_REASONING=true
USE_GROQ_GENERATION=true
USE_GROQ_MATCHING=true

# Model Configuration
REASONING_MODEL=llama3-8b-8192
GENERATION_MODEL=llama3-70b-8192
MATCHING_MODEL=llama3-8b-8192

# Data Configuration
DATA_PATH=data/asia/data.json
DEBUG=false
```

### 3. Start the Servers

**Option A: Automated (Recommended)**
```bash
# Linux/Mac
chmod +x start_servers.sh
./start_servers.sh

# Windows
start_servers.bat
```

**Option B: Manual**
```bash
# Terminal 1: Start Python API
cd cftravel_py
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python api_server.py

# Terminal 2: Start Symfony
symfony server:start --port=8001
```

### 4. Test the Integration

```bash
python test_integration.py
```

### 5. Access the Application

- **Web App**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🧪 Testing the Chat

1. Open http://localhost:8001
2. You should see the chat interface with a welcome message
3. Try these example messages:
   - "Bonjour, je veux partir en voyage"
   - "Je veux partir en Asie en juin"
   - "Cherchez des voyages culturels en Europe"

## 🔧 Troubleshooting

### Python API Issues
```bash
cd cftravel_py
python -c "from concrete_pipeline import LaylaConcreteAgent; agent = LaylaConcreteAgent(); print('Agent loaded successfully')"
```

### Symfony Issues
```bash
symfony server:log
```

### Network Issues
```bash
# Check if Python API is running
curl http://localhost:8000/health

# Check if Symfony is running
curl http://localhost:8001
```

## 📁 Key Files

- `cftravel_py/api_server.py` - Python FastAPI server
- `src/Controller/ChatController.php` - Symfony controller
- `templates/chat/index.html.twig` - Chat interface
- `start_servers.sh` / `start_servers.bat` - Startup scripts
- `test_integration.py` - Integration test

## 🎉 Success Indicators

✅ Both servers start without errors
✅ Web interface loads at http://localhost:8001
✅ Chat interface shows welcome message
✅ Sending a message gets a response from the AI
✅ API documentation is available at http://localhost:8000/docs

## 🚀 Ready to Use!

Once everything is working, you can:
1. Customize the chat interface
2. Add more features to the travel agent
3. Deploy to production
4. Add user authentication
5. Implement conversation history

---

**Need help?** Check the logs or run the test script to diagnose issues. 