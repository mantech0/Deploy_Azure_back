#!/bin/bash

# エラーが発生したら即座に終了
set -e

# 作業ディレクトリを設定
cd /home/site/wwwroot

# ログファイルの設定
LOG_FILE="/home/LogFiles/application.log"
exec 1>>${LOG_FILE}
exec 2>>${LOG_FILE}

echo "$(date -u) - Starting deployment script..."
echo "Current working directory: $(pwd)"
echo "Directory contents:"
ls -la

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

echo "$(date -u) - Starting application..."

# 直接Gunicornを起動（環境変数は使用せず）
exec gunicorn \
    --bind=0.0.0.0:8181 \
    --workers=2 \
    --threads=2 \
    --timeout=120 \
    --log-level=debug \
    --access-logfile=/home/LogFiles/gunicorn_access.log \
    --error-logfile=/home/LogFiles/gunicorn_error.log \
    app:app