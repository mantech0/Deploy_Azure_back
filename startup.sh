#!/bin/bash

# Pythonの仮想環境を作成
python -m venv antenv
source antenv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
gunicorn --bind=0.0.0.0:8000 app:app
