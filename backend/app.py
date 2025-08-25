from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import uuid
from user_manager import UserManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Use threading for Python 3.12 compatibility
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

user_manager = UserManager()

@socketio.on('connect')
def handle_connect():
    print(f'A user connected: {request.sid}')
    user_manager.add_user("randomName", request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f'User disconnected: {request.sid}')
    user_manager.remove_user(request.sid)

@socketio.on('offer')
def handle_offer(data):
    user_manager.room_manager.on_offer(data['roomId'], data['sdp'], request.sid)

@socketio.on('answer')
def handle_answer(data):
    user_manager.room_manager.on_answer(data['roomId'], data['sdp'], request.sid)

@socketio.on('add-ice-candidate')
def handle_ice_candidate(data):
    user_manager.room_manager.on_ice_candidates(data['roomId'], request.sid, data['candidate'], data['type'])

if __name__ == '__main__':
    print("🚀 Starting FreeTalk Server...")
    print("📱 Access URLs:")
    print("   Frontend: http://localhost:5173")
    print("   Backend:  http://localhost:3000")
    print("")

    socketio.run(
        app,
        host='0.0.0.0',
        port=3000,
        debug=False,
        allow_unsafe_werkzeug=False
    )
