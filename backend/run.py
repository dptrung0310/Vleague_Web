# run.py
from app import create_app

# Unpack cả app và socketio
app, socketio = create_app()

if __name__ == '__main__':
    # Dùng socketio.run thay vì app.run để hỗ trợ WebSocket
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)