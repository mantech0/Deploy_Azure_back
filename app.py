import os
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8181))
    print('----------------------------------------')
    print(f'🚀 バックエンドサーバーが起動しました')
    print(f'📡 サーバーURL: http://0.0.0.0:{port}')
    print('----------------------------------------')
    app.run(host='0.0.0.0', port=port)
    
    
