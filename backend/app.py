from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
import uuid
import os
import threading
import time
from user_manager import UserManager
from performance_config import performance_config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Enable CORS for all routes
CORS(app, origins="*")

# Use performance configuration for Socket.IO
socketio = SocketIO(
    app,
    **performance_config.get_socketio_config()
)

user_manager = UserManager()

def cleanup_inactive_users():
    """Periodic cleanup of inactive users and stale rooms"""
    cleanup_config = performance_config.get_cleanup_config()
    while True:
        time.sleep(cleanup_config['cleanup_interval'])
        try:
            user_manager.cleanup_inactive_users()
            user_manager.room_manager.cleanup_stale_rooms()
        except Exception as e:
            print(f"Error in cleanup: {e}")

def monitor_server_performance():
    """Monitor server performance and log statistics"""
    if not performance_config.ENABLE_MONITORING:
        return
        
    while True:
        time.sleep(performance_config.MONITORING_INTERVAL_SECONDS)
        try:
            stats = performance_config.get_server_stats(user_manager, user_manager.room_manager)
            print(f"Server Stats: {stats}")
            
            # Log warnings if server is getting full
            if stats['server_load_percentage'] > 80:
                print(f"⚠️  WARNING: Server load is {stats['server_load_percentage']:.1f}%")
            if stats['room_utilization_percentage'] > 80:
                print(f"⚠️  WARNING: Room utilization is {stats['room_utilization_percentage']:.1f}%")
                
        except Exception as e:
            print(f"Error in monitoring: {e}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_inactive_users, daemon=True)
cleanup_thread.start()

# Start monitoring thread
if performance_config.ENABLE_MONITORING:
    monitoring_thread = threading.Thread(target=monitor_server_performance, daemon=True)
    monitoring_thread.start()

@socketio.on('connect')
def handle_connect():
    print(f'A user connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'User disconnected: {request.sid}')
    user_manager.remove_user(request.sid)

@socketio.on('manual-disconnect')
def handle_manual_disconnect():
    print(f'User manually disconnected: {request.sid}')
    user_manager.remove_user(request.sid)

@socketio.on('join')
def handle_join(data):
    name = data.get('name', 'Anonymous')
    print(f'User {name} ({request.sid}) joining')
    success = user_manager.add_user(name, request.sid)
    if not success:
        emit('error', {'message': 'Failed to join. Please try again.'})

@socketio.on('next')
def handle_next():
    print(f'User requested next: {request.sid}')
    user_manager.next_user(request.sid)

@socketio.on('ready-for-new')
def handle_ready_for_new():
    print(f'User ready for new match: {request.sid}')
    success = user_manager.enqueue_user(request.sid)
    if not success:
        emit('error', {'message': 'Failed to queue. Please try again.'})

@socketio.on('offer')
def handle_offer(data):
    user_manager.update_user_activity(request.sid)
    user_manager.room_manager.on_offer(data['roomId'], data['sdp'], request.sid)

@socketio.on('answer')
def handle_answer(data):
    user_manager.update_user_activity(request.sid)
    user_manager.room_manager.on_answer(data['roomId'], data['sdp'], request.sid)

@socketio.on('add-ice-candidate')
def handle_ice_candidate(data):
    user_manager.update_user_activity(request.sid)
    user_manager.room_manager.on_ice_candidates(data['roomId'], request.sid, data['candidate'], data['type'])

@socketio.on('connection-established')
def handle_connection_established(data):
    user_manager.update_user_activity(request.sid)
    user_manager.room_manager.on_connection_established(data['roomId'], request.sid)

@app.route('/')
def health_check():
    return {'status': 'ok', 'message': 'Buddy Backend is running'}

@app.route('/status')
def queue_status():
    """Debug endpoint to check queue status"""
    status = user_manager.get_queue_status()
    stats = performance_config.get_server_stats(user_manager, user_manager.room_manager)
    room_stats = user_manager.room_manager.get_room_stats()
    return {
        'status': 'ok',
        'queue_status': status,
        'server_stats': stats,
        'room_stats': room_stats,
        'performance_config': {
            'max_concurrent_users': performance_config.MAX_CONCURRENT_USERS,
            'max_rooms': performance_config.MAX_ROOMS,
            'user_timeout': performance_config.USER_TIMEOUT_SECONDS
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print("🚀 Starting Buddy Server...")
    print(f"📱 Backend URL: http://localhost:{port}")
    print(f"👥 Max concurrent users: {performance_config.MAX_CONCURRENT_USERS}")
    print(f"🏠 Max rooms: {performance_config.MAX_ROOMS}")
    print(f"⏰ User timeout: {performance_config.USER_TIMEOUT_SECONDS}s")
    print(f"📊 Monitoring enabled: {performance_config.ENABLE_MONITORING}")
    print("")

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
