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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def read_users_from_csv():
    users = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'users.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # スキルをリストに変換（カンマ区切りの文字列か）
                    skills = row.get('skills', '').split(',') if row.get('skills') else []
                    user = {
                        'id': int(row.get('id', 0)),
                        'name': row.get('name', ''),
                        'email': row.get('email', ''),
                        'skills': [skill.strip() for skill in skills],
                        'experience': row.get('experience', ''),
                        'prefecture': row.get('prefecture', '')
                    }
                    users.append(user)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid user row: {row}, Error: {str(e)}")
                    continue
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found, creating new file")
        # 空のCSVファイルを作成
        write_users_to_csv([])
    except Exception as e:
        print(f"Error reading users CSV: {str(e)}")
        return []
    return users

def write_users_to_csv(users):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'users.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'name', 'email', 'skills', 'experience', 'prefecture'])
            writer.writeheader()
            for user in users:
                # スキルをカンマ区切りの文字列に変換
                user_copy = user.copy()
                user_copy['skills'] = ','.join(str(s) for s in user_copy.get('skills', []))
                writer.writerow(user_copy)
    except Exception as e:
        print(f"Error writing users CSV: {str(e)}")
        raise

def read_projects_from_csv():
    projects = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'projects.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # スキルをリストに変換
                    required_skills = row.get('required_skills', '').split(',') if row.get('required_skills') else []
                    project = {
                        'id': int(row.get('id', 0)),
                        'title': row.get('title', ''),
                        'description': row.get('description', ''),
                        'required_skills': [skill.strip() for skill in required_skills],
                        'location': row.get('location', ''),
                        'duration': row.get('duration', ''),
                        'status': row.get('status', '')
                    }
                    projects.append(project)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid project row: {row}, Error: {str(e)}")
                    continue
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found, creating new file")
        # 空のCSVファイルを作成
        write_projects_to_csv([])
    except Exception as e:
        print(f"Error reading projects CSV: {str(e)}")
        return []
    return projects

def write_projects_to_csv(projects):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'projects.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    try:
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'title', 'description', 'required_skills', 'location', 'duration', 'status'])
            writer.writeheader()
            for project in projects:
                # スキルをカンマ区切りの文字列に変換
                project_copy = project.copy()
                project_copy['required_skills'] = ','.join(str(s) for s in project_copy.get('required_skills', []))
                writer.writerow(project_copy)
    except Exception as e:
        print(f"Error writing projects CSV: {str(e)}")
        raise

def read_assignments_from_csv():
    assignments = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'project_assignments.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                assignment = {
                    'id': int(row['id']),
                    'project_id': int(row['project_id']),
                    'user_id': int(row['user_id']),
                    'assigned_date': row['assigned_date'],
                    'status': row['status']
                }
                assignments.append(assignment)
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found")
        return []
    return assignments

def write_assignments_to_csv(assignments):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'project_assignments.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'project_id', 'user_id', 'assigned_date', 'status'])
        writer.writeheader()
        for assignment in assignments:
            writer.writerow(assignment)

@app.route('/')
@app.route('/health')
def health_check():
    try:
        # データディレクトリとCSVファイルの存在確認
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        data_dir_exists = os.path.exists(data_dir)
        users_csv = os.path.exists(os.path.join(data_dir, 'users.csv'))
        projects_csv = os.path.exists(os.path.join(data_dir, 'projects.csv'))
        assignments_csv = os.path.exists(os.path.join(data_dir, 'project_assignments.csv'))

        return jsonify({
            "message": "Welcome to SkillNow API",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "env": {
                "PORT": os.getenv('PORT'),
                "WEBSITES_PORT": os.getenv('WEBSITES_PORT'),
                "FLASK_ENV": os.getenv('FLASK_ENV'),
                "FRONTEND_URL": FRONTEND_URL,
                "PYTHON_PATH": os.getenv('PYTHONPATH'),
                "WORKING_DIR": os.getcwd()
            },
            "filesystem": {
                "data_dir_exists": data_dir_exists,
                "users_csv_exists": users_csv,
                "projects_csv_exists": projects_csv,
                "assignments_csv_exists": assignments_csv,
                "current_directory": os.listdir('.')
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not Found",
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }), 404

# ユーザー関連のエンドポイント
@api.route('/users', methods=['GET'])
def get_users():
    users = read_users_from_csv()
    response = make_response(json.dumps(users, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    users = read_users_from_csv()
    user = next((user for user in users if user["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "ユーザーが見つかりません"}), 404
    response = make_response(json.dumps(user, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
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
    
    write_users_to_csv(users)
    
    response = make_response(json.dumps(users[user_index], ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/users', methods=['GET'])
def get_users():
    users = read_users_from_csv()
    response = make_response(json.dumps(users, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# プロジェクト関連のエンドポイント
@api.route('/projects', methods=['GET'])
def get_projects():
    projects = read_projects_from_csv()
    response = make_response(json.dumps(projects, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    projects = read_projects_from_csv()
    project = next((project for project in projects if project["id"] == project_id), None)
    if project is None:
        return jsonify({"error": "案件が見つかりません"}), 404
    response = make_response(json.dumps(project, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
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
    
    write_projects_to_csv(projects)
    
    response = make_response(json.dumps(projects[project_index], ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    projects = read_projects_from_csv()
    project_index = next((index for index, project in enumerate(projects) if project["id"] == project_id), None)
    if project_index is None:
        return jsonify({"error": "案件が見つかりません"}), 404
    
    deleted_project = projects.pop(project_index)
    write_projects_to_csv(projects)
    
    return jsonify({"message": "案件を削除しました", "project": deleted_project})

@api.route('/projects', methods=['GET'])
def get_projects():
    projects = read_projects_from_csv()
    response = make_response(json.dumps(projects, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@api.route('/projects', methods=['POST'])
def create_project():
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
    write_projects_to_csv(projects)
    
    response = make_response(json.dumps(new_project, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 201

# 新規ユーザー登録エンドポイントを追加
@api.route('/register', methods=['POST'])
def register_user():
    users = read_users_from_csv()
    data = request.get_json()
    
    # 新しいIDを生成
    new_id = max([user["id"] for user in users], default=0) + 1
    
    new_user = {
        'id': new_id,
        'name': data['name'],
        'email': data['email'],
        'skills': data['skills'],
        'experience': data['experience'],
        'prefecture': data['prefecture']
    }
    
    users.append(new_user)
    write_users_to_csv(users)
    
    response = make_response(json.dumps(new_user, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 201

# プロジェクトに担当者を割り当て
@api.route('/projects/<int:project_id>/assignments', methods=['POST'])
def create_project_assignment(project_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "ユーザーIDが必要です"}), 400
        
    assignments = read_assignments_from_csv()
    
    # 既存の割り当てをチェック
    existing = next((a for a in assignments if a['project_id'] == project_id and a['user_id'] == user_id), None)
    if existing:
        return jsonify({"error": "既に割り当てられています"}), 400
    
    # 新しい割り当てを作成
    new_id = max([a['id'] for a in assignments], default=0) + 1
    new_assignment = {
        'id': new_id,
        'project_id': project_id,
        'user_id': user_id,
        'assigned_date': datetime.now().strftime('%Y-%m-%d'),
        'status': 'active'
    }
    
    assignments.append(new_assignment)
    write_assignments_to_csv(assignments)
    
    response = make_response(json.dumps(new_assignment, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 201

# プロジェクトの担当者を解除
@api.route('/projects/<int:project_id>/assignments/<int:assignment_id>', methods=['DELETE'])
def remove_assignment(project_id, assignment_id):
    assignments = read_assignments_from_csv()
    assignment_index = next((index for index, a in enumerate(assignments) 
                           if a['id'] == assignment_id and a['project_id'] == project_id), None)
    
    if assignment_index is None:
        return jsonify({"error": "割り当てが見つかりません"}), 404
    
    removed = assignments.pop(assignment_index)
    write_assignments_to_csv(assignments)
    
    return jsonify({"message": "割り当てを解除しました", "assignment": removed})

# Blueprintを登録（最後に配置）
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print('----------------------------------------')
    print(f'🚀 バックエンドサーバーが起動しました')
    print(f'📡 サーバーURL: http://0.0.0.0:{port}')
    print('----------------------------------------')
    app.run(host='0.0.0.0', port=port, debug=False) 
    
    
