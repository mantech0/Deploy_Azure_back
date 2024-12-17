#!/bin/bash

# エラーが発生したら即座に終了
set -e

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

# 依存関係のインストール
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "Installed Python packages:"
pip list

# 環境変数の設定
export PORT=8000
export WEBSITES_PORT=8000
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

echo "Current environment:"
env | grep -E 'PORT|FLASK|PYTHON|WEBSITE'

echo "Testing Flask application..."
python -c "
import flask
import werkzeug
print(f'Flask version: {flask.__version__}')
print(f'Werkzeug version: {werkzeug.__version__}')
import app
print('Flask routes:')
for rule in app.app.url_map.iter_rules():
    print(f'  {rule}')"

echo "Starting Gunicorn..."
exec gunicorn \
    --bind=0.0.0.0:8000 \
    --workers=1 \
    --threads=2 \
    --timeout=120 \
    --log-level=debug \
    --access-logfile=- \
    --error-logfile=- \
    --capture-output \
    --enable-stdio-inheritance \
    app:app