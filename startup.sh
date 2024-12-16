#!/bin/bash

# エラーが発生したら即座に終了
set -e

# デバッグモードを有効化
set -x

echo "Starting deployment script..."
echo "Current working directory: $(pwd)"
echo "Directory contents:"
ls -la

# データディレクトリの作成と権限設定
echo "Creating data directory..."
mkdir -p data
chmod 755 data

# CSVファイルの初期化
echo "Initializing CSV files..."
if [ ! -f "data/users.csv" ]; then
    echo "id,name,email,skills,experience,prefecture" > data/users.csv
    echo "Creating empty users.csv"
fi
if [ ! -f "data/projects.csv" ]; then
    echo "id,title,description,required_skills,location,duration,status" > data/projects.csv
    echo "Creating empty projects.csv"
fi
if [ ! -f "data/project_assignments.csv" ]; then
    echo "id,project_id,user_id,assigned_date,status" > data/project_assignments.csv
    echo "Creating empty project_assignments.csv"
fi

# ファイルの存在確認
echo "Checking data directory contents:"
ls -la data/

# 依存関係のインストール
echo "Installing dependencies..."
pip install -r requirements.txt || {
    echo "Failed to install dependencies"
    exit 1
}

# 環境変数の設定
echo "Setting environment variables..."
export PORT=8000
export WEBSITES_PORT=8000
export FLASK_ENV=production
export FLASK_APP=app.py
export PYTHONUNBUFFERED=1

echo "Environment variables:"
env | grep -E 'PORT|FLASK|PYTHON'

echo "Starting application on port: $PORT"

# アプリケーションの起動確認
echo "Testing application import..."
python -c "
import sys
print('Python version:', sys.version)
print('Python path:', sys.path)
import app
print('Application imported successfully')
print('App config:', app.app.config)
" || {
    echo "Failed to import application"
    exit 1
}

# Gunicornの設定ファイルを作成
echo "Creating Gunicorn config..."
cat > gunicorn_config.py << EOL
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "8000")
backlog = 2048

# Worker processes
workers = 1
worker_class = 'sync'
threads = 1
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = 'skill-now-backend'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

def on_starting(server):
    print("Gunicorn is starting up...")

def on_reload(server):
    print("Gunicorn is reloading...")

def when_ready(server):
    print("Gunicorn is ready...")

def on_exit(server):
    print("Gunicorn is shutting down...")
EOL

# Gunicornでアプリケーションを起動
echo "Starting Gunicorn with config file..."
exec gunicorn --config gunicorn_config.py app:app