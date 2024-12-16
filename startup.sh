#!/bin/bash

# デバッグモードを有効化
set -x

echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# データディレクトリの作成と権限設定
mkdir -p data
chmod 755 data

# CSVファイルのコピー
echo "Copying CSV files..."
if [ -d "/home/site/wwwroot/data" ]; then
    cp -f /home/site/wwwroot/data/*.csv data/
else
    echo "Warning: Source data directory not found"
fi

# ファイルの存在確認
echo "Checking CSV files..."
ls -la data/

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
export PORT=8000
export WEBSITES_PORT=8000
export FLASK_ENV=production
export FLASK_APP=app.py

echo "Starting application on port: $PORT"

# アプリケーションの起動確認
python -c "import app; print('Application imported successfully')"

# Gunicornでアプリケーションを起動
exec gunicorn \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --workers 1 \
    --threads 2 \
    --worker-class=gthread \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app