import csv
import os
from flask import Blueprint, jsonify

users_bp = Blueprint('users', __name__, url_prefix='/api')

def load_users():
    users = []
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'users.csv')
    print(f"Loading users from: {csv_path}")
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
        print(f"Loaded {len(users)} users")
        return users
    except Exception as e:
        print(f"Error loading users: {str(e)}")
        return []

@users_bp.route('/users')
def get_users():
    try:
        users = load_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users/<int:user_id>')
def get_user(user_id):
    try:
        users = load_users()
        user = next((user for user in users if user['id'] == user_id), None)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500