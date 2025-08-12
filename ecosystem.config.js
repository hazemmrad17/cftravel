module.exports = {
  apps: [{
    name: 'cftravel-api',
    script: 'python',
    args: '-m uvicorn api.server:app --host 0.0.0.0 --port 8001',
    cwd: './cftravel_py',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 8001
    },
    error_file: './logs/api-error.log',
    out_file: './logs/api-out.log',
    log_file: './logs/api-combined.log',
    time: true
  }]
}; 