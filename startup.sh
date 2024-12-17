#!/bin/bash

# エラーが発生したら即座に終了
set -e

# ログファイルの設定
LOG_FILE="/home/LogFiles/application.log"
exec 1>>${LOG_FILE}
exec 2>>${LOG_FILE}

echo "$(date -u) - Starting deployment script..."
echo "Current working directory: $(pwd)"
echo "Directory contents:"
ls -la

# スクリプトの実行権限を確認
echo "$(date -u) - Checking script permissions..."
chmod +x "$(dirname "$0")/startup.sh"

# Pythonのバージョンを確認
echo "$(date -u) - Python version:"
python --version
which python

# 環境変数を確認
echo "$(date -u) - Environment variables:"
env | sort

# データディレクトリの作成と権限設定
echo "$(date -u) - Creating data directory..."
mkdir -p data
chmod 755 data

# CSVファイルの初期化
echo "$(date -u) - Initializing CSV files..."
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

# 依存関係のインストール
echo "$(date -u) - Installing dependencies..."
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "$(date -u) - Installed Python packages:"
pip list

# 環境変数の設定
export PORT=8181
export WEBSITES_PORT=8181
export FLASK_APP=app
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export PYTHONPATH=/home/site/wwwroot

echo "$(date -u) - Current environment:"
env | grep -E 'PORT|FLASK|PYTHON|WEBSITE'

echo "$(date -u) - Testing Flask application..."
python -c "
import flask
import werkzeug
print(f'Flask version: {flask.__version__}')
print(f'Werkzeug version: {werkzeug.__version__}')
from app import app
print('Flask routes:')
for rule in app.url_map.iter_rules():
    print(f'  {rule}')"

echo "$(date -u) - Starting Gunicorn..."
cd "$(dirname "$0")"
exec gunicorn \
    --bind=0.0.0.0:8181 \
    --workers=1 \
    --threads=2 \
    --timeout=120 \
    --log-level=debug \
    --access-logfile=/home/LogFiles/gunicorn_access.log \
    --error-logfile=/home/LogFiles/gunicorn_error.log \
    --capture-output \
    --enable-stdio-inheritance \
    --reload \
    app:app