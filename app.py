from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
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
    app.run(debug=True, port=5000) 