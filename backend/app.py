from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
import uuid
import os
from user_manager import UserManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Enable CORS for all routes
CORS(app, origins="*")

# Use threading for Python 3.13 compatibility
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

@socketio.on('manual-disconnect')
def handle_manual_disconnect():
    print(f'User manually disconnected: {request.sid}')
    user_manager.remove_user(request.sid)

@socketio.on('next')
def handle_next():
    print(f'User requested next: {request.sid}')
    user_manager.next_user(request.sid)

@socketio.on('ready-for-new')
def handle_ready_for_new():
    print(f'User ready for new match: {request.sid}')
    user_manager.enqueue_user(request.sid)

@socketio.on('offer')
def handle_offer(data):
    user_manager.room_manager.on_offer(data['roomId'], data['sdp'], request.sid)

@socketio.on('answer')
def handle_answer(data):
    user_manager.room_manager.on_answer(data['roomId'], data['sdp'], request.sid)

@socketio.on('add-ice-candidate')
def handle_ice_candidate(data):
    user_manager.room_manager.on_ice_candidates(data['roomId'], request.sid, data['candidate'], data['type'])

@app.route('/')
def health_check():
    return {'status': 'ok', 'message': 'Buddy Backend is running'}

@app.route('/status')
def queue_status():
    """Debug endpoint to check queue status"""
    status = user_manager.get_queue_status()
    return {
        'status': 'ok',
        'queue_status': status,
        'active_rooms': len(user_manager.room_manager.rooms)
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print("🚀 Starting Buddy Server...")
    print(f"📱 Backend URL: http://localhost:{port}")
    print("")

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
