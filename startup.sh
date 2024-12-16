#!/bin/bash

# デバッグモードを有効化
set -x

echo "Starting deployment script..."
echo "Python version:"
python --version
echo "Pip version:"
pip --version

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# データディレクトリの作成と権限設定
echo "Creating data directory..."
mkdir -p data
chmod 755 data

# CSVファイルのコピー
echo "Copying CSV files..."
if [ -d "/home/site/wwwroot/data" ]; then
    echo "Source data directory exists"
    ls -la /home/site/wwwroot/data/
    cp -f /home/site/wwwroot/data/*.csv data/ || echo "Warning: CSV copy failed"
else
    echo "Warning: Source data directory not found at /home/site/wwwroot/data"
    echo "Current directory structure:"
    find /home/site/wwwroot -type d
fi

# ファイルの存在確認
echo "Checking data directory contents:"
ls -la data/

# 依存関係のインストール
echo "Installing dependencies..."
pip install -r requirements.txt

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
print('Python path:', sys.path)
import app
print('Application imported successfully')
print('App config:', app.app.config)
" || exit 1

echo "Testing application startup..."
timeout 30s python -c "
import sys
print('Python path:', sys.path)
from app import app
print('Creating test client...')
with app.test_client() as client:
    print('Sending health check request...')
    response = client.get('/health')
    print(f'Health check response: {response.status_code}')
    print(f'Response data: {response.data}')
    if response.status_code != 200:
        raise Exception('Health check failed')
    print('Health check passed')
" || exit 1

# データディレクトリの権限を確認
echo "Checking data directory permissions..."
ls -la data/

# Gunicornでアプリケーションを起動
echo "Starting Gunicorn..."
exec gunicorn \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --workers 1 \
    --threads 2 \
    --worker-class=gthread \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --preload \
    --worker-tmp-dir /dev/shm \
    --graceful-timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    app:app