#!/bin/bash

# デバッグ情報の出力
set -x

# カレントディレクトリの確認
pwd
ls -la

# 依存関係のインストール
pip install -r requirements.txt

# データディレクトリの作成とCSVファイルのコピー
mkdir -p data
cp -f data/*.csv data/ || echo "Warning: CSV copy failed"

# CSVファイルの存在確認
echo "Checking CSV files..."
ls -la data/

# 環境変数の設定
if [ -n "$WEBSITES_PORT" ]; then
    export PORT=$WEBSITES_PORT
else
    export PORT=8000
fi

# デバッグ情報
echo "Debug Information:"
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"
echo "Files in data directory: $(ls -la data)"
echo "PORT: $PORT"
echo "WEBSITES_PORT: $WEBSITES_PORT"
echo "PYTHON_VERSION: $PYTHON_VERSION"

# アプリケーションの起動
echo "Starting Gunicorn on port $PORT..."
exec gunicorn \
    --bind=0.0.0.0:$PORT \
    --timeout 600 \
    --workers 1 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    app:app