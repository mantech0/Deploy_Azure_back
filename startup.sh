#!/bin/bash

# デバッグモードを有効化
set -x

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# データディレクトリの作成
mkdir -p data

# CSVファイルの存在確認
if [ ! -f "data/users.csv" ] || [ ! -f "data/projects.csv" ] || [ ! -f "data/project_assignments.csv" ]; then
    echo "Copying CSV files..."
    cp -r /home/site/wwwroot/data/* data/
fi

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
export PORT=8000
export WEBSITES_PORT=8000

echo "Starting application on port: $PORT"

# Gunicornでアプリケーションを起動
exec gunicorn \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --workers 2 \
    --threads 2 \
    --worker-class=gthread \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --reload \
    app:app