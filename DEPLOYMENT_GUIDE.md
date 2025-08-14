# 🚀 Production Deployment Guide

## Quick Deployment

1. **Set up Git remote** (if not already done):
```bash
git remote add iagent ssh://git-iagent@146.59.242.69:/var/repo/iagent.cftravel.net.git
```

2. **Run deployment script**:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Manual Deployment

1. **Set production environment**:
```bash
cp env.production .env
```

2. **Add and commit changes**:
```bash
git add .
git commit -m "🚀 Production deployment: $(date)"
```

3. **Push to production**:
```bash
git push -u iagent master
```

## Production URLs

- **Main Domain**: https://asia-iagent.cftravel.net
- **Alias**: https://ovg-iagent.cftravel.net

## Server Configuration

The server automatically runs `server.py` when you push to the repository.

## Environment Variables

Make sure to update `env.production` with your actual API keys:
- `GROQ_API_KEY`
- `MOONSHOT_API_KEY`
- `APP_SECRET`

## Troubleshooting

If deployment fails:
1. Check your SSH key is added to the server
2. Verify the Git remote is correct
3. Ensure all files are committed 