from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import json
import csv
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://tech0-gen-8-step3-testapp-node2-26.azurewebsites.net"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# ポート設定を環境変数から取得するように変更
import os
PORT = int(os.getenv('PORT', 8000))

def read_users_from_csv():
    users = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'users.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # スキルをリストに変換（カンマ区切りの文字列から）
                skills = row.get('skills', '').split(',') if row.get('skills') else []
                user = {
                    'id': int(row['id']),
                    'name': row['name'],
                    'email': row['email'],
                    'skills': [skill.strip() for skill in skills],
                    'experience': row['experience'],
                    'prefecture': row['prefecture']
                }
                users.append(user)
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found")
        return []
    return users

def write_users_to_csv(users):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'users.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)  # データディレクトリがない場合は作成
    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'name', 'email', 'skills', 'experience', 'prefecture'])
        writer.writeheader()
        for user in users:
            # スキルをカンマ区切りの文字列に変換
            user_copy = user.copy()
            user_copy['skills'] = ','.join(user_copy['skills'])
            writer.writerow(user_copy)

def read_projects_from_csv():
    projects = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'projects.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # スキルをリストに変換
                required_skills = row.get('required_skills', '').split(',') if row.get('required_skills') else []
                project = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'description': row['description'],
                    'required_skills': [skill.strip() for skill in required_skills],
                    'location': row['location'],
                    'duration': row['duration'],
                    'status': row['status']
                }
                projects.append(project)
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found")
        return []
    return projects

def write_projects_to_csv(projects):
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'projects.csv')
    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'description', 'required_skills', 'location', 'duration', 'status'])
        writer.writeheader()
        for project in projects:
            # スキルをカンマ区切りの文字列に変換
            project_copy = project.copy()
            project_copy['required_skills'] = ','.join(project_copy['required_skills'])
            writer.writerow(project_copy)

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
def home():
    return jsonify({"message": "Welcome to SkillNow API"})

# ユーザー関連のエンドポイント
@app.route('/api/users', methods=['GET'])
def get_users():
    users = read_users_from_csv()
    response = make_response(json.dumps(users, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    users = read_users_from_csv()
    user = next((user for user in users if user["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "ユーザーが見つかりません"}), 404
    response = make_response(json.dumps(user, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/users/<int:user_id>', methods=['PUT'])
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
    
    # CSVファイルに保存
    write_users_to_csv(users)
    
    response = make_response(json.dumps(users[user_index], ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# 案件関連のエンドポイント
@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = read_projects_from_csv()
    response = make_response(json.dumps(projects, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    projects = read_projects_from_csv()
    project = next((project for project in projects if project["id"] == project_id), None)
    if project is None:
        return jsonify({"error": "案件が見つかりません"}), 404
    response = make_response(json.dumps(project, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/projects', methods=['POST'])
def create_project():
    projects = read_projects_from_csv()
    data = request.get_json()
    
    # 新しいIDを生成
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

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
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

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    projects = read_projects_from_csv()
    project_index = next((index for index, project in enumerate(projects) if project["id"] == project_id), None)
    if project_index is None:
        return jsonify({"error": "案件が見つかりません"}), 404
    
    deleted_project = projects.pop(project_index)
    write_projects_to_csv(projects)
    
    return jsonify({"message": "案件を削除しました", "project": deleted_project})

# 新規ユーザー登録エンドポイントを追加
@app.route('/api/register', methods=['POST'])
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

# プロジェクトの担当者情報を取得
@app.route('/api/projects/<int:project_id>/assignments', methods=['GET'])
def get_project_assignments(project_id):
    assignments = read_assignments_from_csv()
    project_assignments = [a for a in assignments if a['project_id'] == project_id]
    
    # 担当者の詳細情報を取得
    users = read_users_from_csv()
    for assignment in project_assignments:
        user = next((u for u in users if u['id'] == assignment['user_id']), None)
        if user:
            assignment['user'] = user

    response = make_response(json.dumps(project_assignments, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# ユーザーの担当プロジェクト情報を取得
@app.route('/api/users/<int:user_id>/assignments', methods=['GET'])
def get_user_assignments(user_id):
    assignments = read_assignments_from_csv()
    user_assignments = [a for a in assignments if a['user_id'] == user_id]
    
    # プロジェクトの詳細情報を取得
    projects = read_projects_from_csv()
    for assignment in user_assignments:
        project = next((p for p in projects if p['id'] == assignment['project_id']), None)
        if project:
            assignment['project'] = project

    response = make_response(json.dumps(user_assignments, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# プロジェクトに担当者を割り当て
@app.route('/api/projects/<int:project_id>/assignments', methods=['POST'])
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
@app.route('/api/projects/<int:project_id>/assignments/<int:assignment_id>', methods=['DELETE'])
def remove_assignment(project_id, assignment_id):
    assignments = read_assignments_from_csv()
    assignment_index = next((index for index, a in enumerate(assignments) 
                           if a['id'] == assignment_id and a['project_id'] == project_id), None)
    
    if assignment_index is None:
        return jsonify({"error": "割り当てが見つかりません"}), 404
    
    removed = assignments.pop(assignment_index)
    write_assignments_to_csv(assignments)
    
    return jsonify({"message": "割り当てを解除しました", "assignment": removed})

if __name__ == '__main__':
    print('----------------------------------------')
    print(f'🚀 バックエンドサーバーが起動しました')
    print(f'📡 サーバーURL: http://localhost:{PORT}')
    print('----------------------------------------')
    app.run(host='0.0.0.0', port=PORT) 
    
