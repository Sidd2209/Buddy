"""
Performance configuration for Buddy video chat application
Handles server resources, connection limits, and optimization settings
"""

import os

class PerformanceConfig:
    def __init__(self):
        # Server capacity settings
        self.MAX_CONCURRENT_USERS = int(os.environ.get('MAX_CONCURRENT_USERS', 200))
        self.MAX_ROOMS = int(os.environ.get('MAX_ROOMS', 100))
        self.USER_TIMEOUT_SECONDS = int(os.environ.get('USER_TIMEOUT_SECONDS', 300))  # 5 minutes
        
        # WebRTC optimization
        self.ICE_SERVERS = [
            {'urls': 'stun:stun.l.google.com:19302'},
            {'urls': 'stun:stun1.l.google.com:19302'},
            {'urls': 'stun:stun2.l.google.com:19302'},
            {'urls': 'stun:stun3.l.google.com:19302'},
            {'urls': 'stun:stun4.l.google.com:19302'}
        ]
        
        # Socket.IO settings
        self.SOCKET_PING_TIMEOUT = int(os.environ.get('SOCKET_PING_TIMEOUT', 60))
        self.SOCKET_PING_INTERVAL = int(os.environ.get('SOCKET_PING_INTERVAL', 25))
        self.SOCKET_MAX_HTTP_BUFFER_SIZE = int(os.environ.get('SOCKET_MAX_HTTP_BUFFER_SIZE', 1e6))
        
        # Cleanup intervals
        self.CLEANUP_INTERVAL_SECONDS = int(os.environ.get('CLEANUP_INTERVAL_SECONDS', 60))
        self.ROOM_CLEANUP_INTERVAL_SECONDS = int(os.environ.get('ROOM_CLEANUP_INTERVAL_SECONDS', 300))
        
        # Performance monitoring
        self.ENABLE_MONITORING = os.environ.get('ENABLE_MONITORING', 'true').lower() == 'true'
        self.MONITORING_INTERVAL_SECONDS = int(os.environ.get('MONITORING_INTERVAL_SECONDS', 30))
        
    def get_socketio_config(self):
        """Get Socket.IO configuration for optimal performance"""
        return {
            'cors_allowed_origins': "*",
            'async_mode': 'threading',
            'logger': False,
            'engineio_logger': False,
            'ping_timeout': self.SOCKET_PING_TIMEOUT,
            'ping_interval': self.SOCKET_PING_INTERVAL,
            'max_http_buffer_size': self.SOCKET_MAX_HTTP_BUFFER_SIZE,
            'allow_upgrades': True,
            'transports': ['websocket', 'polling']
        }
    
    def get_webrtc_config(self):
        """Get WebRTC configuration for optimal performance"""
        return {
            'iceServers': self.ICE_SERVERS,
            'iceCandidatePoolSize': 10,
            'bundlePolicy': 'max-bundle',
            'rtcpMuxPolicy': 'require',
            'iceTransportPolicy': 'all'
        }
    
    def get_server_stats(self, user_manager, room_manager):
        """Get current server statistics"""
        return {
            'total_users': len(user_manager.users),
            'queue_length': len(user_manager.queue),
            'active_rooms': room_manager.get_room_count(),
            'max_concurrent_users': self.MAX_CONCURRENT_USERS,
            'max_rooms': self.MAX_ROOMS,
            'server_load_percentage': (len(user_manager.users) / self.MAX_CONCURRENT_USERS) * 100,
            'room_utilization_percentage': (room_manager.get_room_count() / self.MAX_ROOMS) * 100
        }
    
    def should_accept_new_user(self, user_manager, room_manager):
        """Check if server can accept new users"""
        return (
            len(user_manager.users) < self.MAX_CONCURRENT_USERS and
            room_manager.get_room_count() < self.MAX_ROOMS
        )
    
    def get_cleanup_config(self):
        """Get cleanup configuration"""
        return {
            'user_timeout': self.USER_TIMEOUT_SECONDS,
            'cleanup_interval': self.CLEANUP_INTERVAL_SECONDS,
            'room_cleanup_interval': self.ROOM_CLEANUP_INTERVAL_SECONDS
        }

# Global performance configuration instance
performance_config = PerformanceConfig()
