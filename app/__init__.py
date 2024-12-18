from flask import Flask, jsonify, request, make_response, Blueprint
from flask_cors import CORS
import json
import csv
import os
from datetime import datetime

app = Flask(__name__)
api = Blueprint('api', __name__)

# CORSの設定
FRONTEND_URL = "https://tech0-gen-8-step3-testapp-node2-26.azurewebsites.net"
CORS(app, resources={
    r"/*": {
        "origins": [FRONTEND_URL, "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"]
    }
})

# データディレクトリの設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def read_users_from_csv():
    users = []
    csv_path = os.path.join(DATA_DIR, 'users.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append({
                    'id': int(row['id']),
                    'email': row['email'],
                    'name': row['name'],
                    'skills': row.get('skills', '').split(',') if row.get('skills') else [],
                    'experience': row.get('experience', ''),
                    'prefecture': row['prefecture']
                })
        return users
    except Exception as e:
        print(f"Error reading users CSV: {str(e)}")
        return []

def write_users_to_csv(users):
    csv_path = os.path.join(DATA_DIR, 'users.csv')
    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            fieldnames = ['id', 'email', 'name', 'skills', 'experience', 'prefecture']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                user_data = {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'skills': ','.join(user['skills']) if user['skills'] else '',
                    'experience': user['experience'],
                    'prefecture': user['prefecture']
                }
                writer.writerow(user_data)
        return True
    except Exception as e:
        print(f"Error writing users CSV: {str(e)}")
        return False

def read_projects_from_csv():
    projects = []
    csv_path = os.path.join(DATA_DIR, 'projects.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                projects.append({
                    'id': int(row['id']),
                    'title': row['title'],
                    'description': row['description'],
                    'required_skills': row.get('required_skills', '').split(',') if row.get('required_skills') else [],
                    'location': row['location'],
                    'duration': row['duration'],
                    'status': row['status']
                })
        return projects
    except Exception as e:
        print(f"Error reading projects CSV: {str(e)}")
        return []

def write_projects_to_csv(projects):
    csv_path = os.path.join(DATA_DIR, 'projects.csv')
    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            fieldnames = ['id', 'title', 'description', 'required_skills', 'location', 'duration', 'status']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for project in projects:
                project_data = {
                    'id': project['id'],
                    'title': project['title'],
                    'description': project['description'],
                    'required_skills': ','.join(project['required_skills']) if project['required_skills'] else '',
                    'location': project['location'],
                    'duration': project['duration'],
                    'status': project['status']
                }
                writer.writerow(project_data)
        return True
    except Exception as e:
        print(f"Error writing projects CSV: {str(e)}")
        return False

# ヘルスチェックエンドポイント
@app.route('/')
@app.route('/health')
def health_check():
    try:
        return jsonify({
            "message": "Welcome to SkillNow API",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ユーザー関連のエンドポイント
@api.route('/users', methods=['GET'])
def get_users():
    try:
        print(f"Loading users from: {os.path.join(DATA_DIR, 'users.csv')}")
        users = read_users_from_csv()
        print(f"Loaded {len(users)} users")
        response = make_response(json.dumps(users, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        users = read_users_from_csv()
        user = next((user for user in users if user["id"] == user_id), None)
        if user is None:
            return jsonify({"error": "ユーザーが見つかりません"}), 404
        response = make_response(json.dumps(user, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        users = read_users_from_csv()
        user_index = next((index for index, user in enumerate(users) if user["id"] == user_id), None)
        if user_index is None:
            return jsonify({"error": "ユーザーが見つかりません"}), 404

        data = request.get_json()
        users[user_index].update({
            'name': data['name'],
            'email': data['email'],
            'skills': data['skills'],
            'experience': data['experience'],
            'prefecture': data['prefecture']
        })

        if write_users_to_csv(users):
            response = make_response(json.dumps(users[user_index], ensure_ascii=False))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response
        else:
            return jsonify({"error": "ユーザー情報の更新に失敗しました"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# プロジェクト関連のエンドポイント
@api.route('/projects', methods=['GET'])
def get_projects():
    try:
        print(f"Loading projects from: {os.path.join(DATA_DIR, 'projects.csv')}")
        projects = read_projects_from_csv()
        print(f"Loaded {len(projects)} projects")
        response = make_response(json.dumps(projects, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    try:
        projects = read_projects_from_csv()
        project = next((project for project in projects if project["id"] == project_id), None)
        if project is None:
            return jsonify({"error": "案件が見つかりません"}), 404
        response = make_response(json.dumps(project, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/projects', methods=['POST'])
def create_project():
    try:
        projects = read_projects_from_csv()
        data = request.get_json()

        new_id = max([project["id"] for project in projects], default=0) + 1
        new_project = {
            'id': new_id,
            'title': data['title'],
            'description': data['description'],
            'required_skills': data['required_skills'],
            'location': data['location'],
            'duration': data['duration'],
            'status': data['status']
        }

        projects.append(new_project)
        if write_projects_to_csv(projects):
            response = make_response(json.dumps(new_project, ensure_ascii=False))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 201
        else:
            return jsonify({"error": "案件の作成に失敗しました"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        projects = read_projects_from_csv()
        project_index = next((index for index, project in enumerate(projects) if project["id"] == project_id), None)
        if project_index is None:
            return jsonify({"error": "案件が見つかりません"}), 404

        data = request.get_json()
        projects[project_index].update({
            'title': data['title'],
            'description': data['description'],
            'required_skills': data['required_skills'],
            'location': data['location'],
            'duration': data['duration'],
            'status': data['status']
        })

        if write_projects_to_csv(projects):
            response = make_response(json.dumps(projects[project_index], ensure_ascii=False))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response
        else:
            return jsonify({"error": "案件の更新に失敗しました"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Blueprintを登録
app.register_blueprint(api, url_prefix='/api')
