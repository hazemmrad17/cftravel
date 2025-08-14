# 🚀 ASIA.fr Agent - Production Setup Guide

## 📋 **Quick Setup for Production**

### **1. Environment Configuration**

On your production server (`ovg-iagent.cftravel.net`), create the `.env` file:

```bash
# Copy the production template
cp env.production .env

# Edit the .env file with your actual values
nano .env
```

**Required changes in `.env`:**
```bash
# Replace with your actual Groq API key
GROQ_API_KEY=your_actual_groq_api_key_here

# Set environment to production
ENVIRONMENT=production
DEBUG=false
APP_ENV=prod

# Change the app secret
APP_SECRET=your_actual_app_secret_here
```

### **2. Server Configuration**

Make sure your server has:
- **Port 8000** available for the Python API
- **Port 443** (HTTPS) for the frontend
- **PHP 8.1+** installed
- **Python 3.9+** installed

### **3. Start Services**

```bash
# Start Python API (background)
cd cftravel_py
python -m api.server &

# Start Symfony (background)
symfony server:start --port=8001 --daemon
```

### **4. Verify Configuration**

Check that:
- ✅ Frontend loads at `https://ovg-iagent.cftravel.net`
- ✅ API responds at `https://ovg-iagent.cftravel.net/api/config`
- ✅ Chat works for all users
- ✅ No CORS errors in browser console

## 🔧 **Troubleshooting**

### **If it only works for you:**

1. **Check environment variables:**
   ```bash
   echo $ENVIRONMENT
   echo $GROQ_API_KEY
   ```

2. **Verify API is running:**
   ```bash
   curl http://localhost:8000/status
   ```

3. **Check Symfony logs:**
   ```bash
   tail -f var/log/dev.log
   ```

4. **Check Python API logs:**
   ```bash
   # Look for any error messages in the Python API output
   ```

### **Common Issues:**

- **CORS errors:** Make sure `ovg-iagent.cftravel.net` is in the allowed origins
- **API not responding:** Check if Python API is running on port 8000
- **Configuration not loading:** Verify `.env` file exists and has correct values

## 🌐 **URL Structure**

- **Frontend:** `https://ovg-iagent.cftravel.net`
- **API Proxy:** `https://ovg-iagent.cftravel.net/api/*`
- **Python Backend:** `http://localhost:8000` (internal)

## 📝 **Configuration Files**

- **`.env`** - Environment variables (create from `env.production`)
- **`config/app.php`** - Application configuration
- **`public/assets/js/config/unified-config.js`** - Frontend configuration

## 🔄 **Deployment Commands**

```bash
# Pull latest changes
git pull origin main

# Install dependencies
composer install --no-dev --optimize-autoloader
npm install --production

# Clear caches
php bin/console cache:clear --env=prod

# Restart services
# (Restart Python API and Symfony)
```

## ✅ **Verification Checklist**

- [ ] `.env` file exists with correct values
- [ ] `ENVIRONMENT=production` is set
- [ ] `GROQ_API_KEY` is valid
- [ ] Python API is running on port 8000
- [ ] Symfony is running and accessible
- [ ] Frontend loads without errors
- [ ] Chat works for multiple users
- [ ] No CORS errors in browser console
- [ ] API endpoints respond correctly

## 🆘 **Need Help?**

If you're still having issues:
1. Check the browser console for errors
2. Verify all environment variables are set
3. Ensure both services (Python + Symfony) are running
4. Check server logs for any error messages 