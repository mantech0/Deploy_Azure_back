from flask import Flask, jsonify
from flask_cors import CORS
from .routes.users import users_bp

app = Flask(__name__)

# CORS設定を詳細に指定
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://tech0-gen-8-step3-testapp-node2-26.azurewebsites.net"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# ルートの登録
app.register_blueprint(users_bp)

@app.route('/')
def index():
    try:
        return jsonify({
            'message': 'Welcome to SkillNow API',
            'status': 'running'
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
