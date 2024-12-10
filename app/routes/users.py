import csv
import os
from flask import Blueprint, jsonify

users_bp = Blueprint('users', __name__)

def load_users():
    users = []
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users.csv')
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append({
                    'id': row['id'],
                    'email': row['email'],
                    'name': row['name'],
                    'prefecture': row['prefecture']
                })
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

@users_bp.route('/users/<user_id>')
def get_user(user_id):
    try:
        users = load_users()
        user = next((user for user in users if user['id'] == user_id), None)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500