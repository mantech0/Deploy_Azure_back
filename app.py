from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://*.azurewebsites.net"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/v1/projects', methods=['GET'])
def get_projects():
    # テスト用のダミーデータ
    projects = [
        {
            "id": 1,
            "title": "テストプロジェクト",
            "description": "これはテスト用のプロジェクトです",
            "budget": 100000,
            "status": "進行中"
        }
    ]
    return jsonify(projects)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', debug=True, port=port) 