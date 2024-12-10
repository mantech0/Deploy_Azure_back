from flask import Blueprint, jsonify

bp = Blueprint('projects', __name__, url_prefix='/api/v1/projects')

@bp.route('/', methods=['GET'])
def get_projects():
    # テストデータ
    projects = [
        {
            'id': 1,
            'title': 'Webアプリケーション開発',
            'description': 'React/Next.jsを使用したフロントエンド開発',
            'budget': 500000,
            'status': '募集中',
            'created_at': '2024-03-20',
            'user_id': 1
        },
        {
            'id': 2,
            'title': 'モバイルアプリ開発',
            'description': 'Flutter/Dartを使用したクロスプラットフォーム開発',
            'budget': 800000,
            'status': '募集中',
            'created_at': '2024-03-21',
            'user_id': 2
        }
    ]
    return jsonify(projects) 