from flask_socketio import emit
from room_manager import RoomManager
from performance_config import performance_config
import threading
import time
import random

class UserManager:
    def __init__(self):
        self.users = {}  # socket_id -> user_data
        self.queue = []
        self.room_manager = RoomManager()
        self.lock = threading.Lock()  # Thread safety for queue operations
        
        # Use performance config
        self.max_concurrent_users = performance_config.MAX_CONCURRENT_USERS
        self.user_timeout = performance_config.USER_TIMEOUT_SECONDS
        
        # Connection tracking
        self.connection_attempts = {}  # socket_id -> attempt_count
        self.max_connection_attempts = 3

    def add_user(self, name, socket_id):
        with self.lock:
            # Check if we're at capacity
            if not performance_config.should_accept_new_user(self, self.room_manager):
                emit("error", {"message": "Server is at capacity. Please try again later."}, room=socket_id)
                return False
            
            # Check if user already exists
            if socket_id in self.users:
                print(f"User {socket_id} already exists")
                return False
            
            # Add user to users dict
            self.users[socket_id] = {
                "name": name, 
                "socket_id": socket_id, 
                "state": "queue",
                "timestamp": time.time(),
                "connection_attempts": 0,
                "last_activity": time.time()
            }
            
            # Add to queue
            if socket_id not in self.queue:
                self.queue.append(socket_id)
                print(f"User {name} ({socket_id}) added to queue. Queue length: {len(self.queue)}")
            
            emit("lobby", room=socket_id)
            self.process_queue()
        return True

    def enqueue_user(self, socket_id):
        with self.lock:
            # Check if user exists
            if socket_id not in self.users:
                print(f"User {socket_id} not found in users")
                return False
                
            user = self.users[socket_id]
            current_state = user.get("state", "unknown")
            
            # Reset connection attempts when re-enqueueing
            user["connection_attempts"] = 0
            user["last_activity"] = time.time()
            
            # Only enqueue if user is not already queued and not in a room
            if current_state == "queue" and socket_id in self.queue:
                print(f"User {socket_id} already in queue")
                return False
                
            if current_state == "room":
                print(f"User {socket_id} is in a room, cannot enqueue")
                return False
            
            # Update user state and add to queue
            user["state"] = "queue"
            user["timestamp"] = time.time()
            if socket_id not in self.queue:
                self.queue.append(socket_id)
                print(f"User {socket_id} enqueued. Queue length: {len(self.queue)}")
                emit("lobby", room=socket_id)
                self.process_queue()
            return True

    def next_user(self, socket_id):
        """
        Omegle-style next: immediately disconnect from current partner and find new match
        """
        with self.lock:
            # Find the room
            room_id, room = self.room_manager.get_room_by_user(socket_id)
            if room:
                # User is in a room - proceed with next
                print(f"User {socket_id} requested next from room {room_id}")
                
                # Identify partner
                if room["user1_socket"] == socket_id:
                    partner_socket = room["user2_socket"]
                    partner_name = room["user2"]["name"]
                else:
                    partner_socket = room["user1_socket"]
                    partner_name = room["user1"]["name"]

                # Update user states
                if socket_id in self.users:
                    self.users[socket_id]["state"] = "queue"
                    self.users[socket_id]["timestamp"] = time.time()
                    self.users[socket_id]["connection_attempts"] = 0
                if partner_socket in self.users:
                    self.users[partner_socket]["state"] = "queue"
                    self.users[partner_socket]["timestamp"] = time.time()
                    self.users[partner_socket]["connection_attempts"] = 0

                # Remove room and notify both sides appropriately
                self.room_manager.remove_room(room_id)
                emit("partner-disconnected", room=partner_socket)

                # Enqueue both users for new matches
                self.enqueue_user(socket_id)
                self.enqueue_user(partner_socket)
            else:
                # User is not in a room (just waiting in queue) - ignore next request
                print(f"User {socket_id} requested next but is not in a room (just waiting)")

    def remove_user(self, socket_id):
        with self.lock:
            # First, handle room disconnection
            remaining_user = self.room_manager.handle_user_disconnect(socket_id)
            
            # Remove user from users dict
            if socket_id in self.users:
                user_name = self.users[socket_id].get("name", "Unknown")
                del self.users[socket_id]
                print(f"User {user_name} ({socket_id}) removed")
            
            # Remove user from queue if they're in it
            if socket_id in self.queue:
                self.queue.remove(socket_id)
            
            # If there's a remaining user from a room, add them back to queue
            if remaining_user:
                remaining_socket_id = remaining_user["socket_id"]
                print(f"User {remaining_socket_id} returned to queue after partner disconnected")
                
                # Update remaining user's state
                if remaining_socket_id in self.users:
                    self.users[remaining_socket_id]["state"] = "queue"
                    self.users[remaining_socket_id]["timestamp"] = time.time()
                    self.users[remaining_socket_id]["connection_attempts"] = 0
                
                # Add to queue if not already there
                if remaining_socket_id not in self.queue:
                    self.queue.append(remaining_socket_id)
                    emit("lobby", room=remaining_socket_id)
                    self.process_queue()
            
            print(f"Queue length after removal: {len(self.queue)}")

    def process_queue(self):
        """
        Process the queue to pair users efficiently
        """
        print(f"Processing queue. Length: {len(self.queue)}")

        # Keep processing until we can't make more pairs
        while len(self.queue) >= 2:
            # Get two users from queue (FIFO)
            id1 = self.queue.pop(0)
            id2 = self.queue.pop(0)
            
            # Verify both users still exist and are in queue state
            if id1 not in self.users or id2 not in self.users:
                print("Pairing failed: One or both users not found in users dict.")
                # Put users back in queue if pairing failed
                if id1 in self.users:
                    self.queue.insert(0, id1)
                if id2 in self.users:
                    self.queue.insert(0, id2)
                break

            user1 = self.users[id1]
            user2 = self.users[id2]

            # Check if users are in correct state
            if user1.get("state") != "queue" or user2.get("state") != "queue":
                print("Pairing failed: Users not in queue state.")
                # Put users back in queue
                self.queue.insert(0, id1)
                self.queue.insert(0, id2)
                break

            # Check connection attempts
            if user1.get("connection_attempts", 0) >= self.max_connection_attempts:
                print(f"User {id1} has exceeded connection attempts, skipping")
                self.queue.append(id1)  # Put back at end
                continue
                
            if user2.get("connection_attempts", 0) >= self.max_connection_attempts:
                print(f"User {id2} has exceeded connection attempts, skipping")
                self.queue.append(id2)  # Put back at end
                continue

            # Update user states to room
            user1["state"] = "room"
            user2["state"] = "room"
            user1["connection_attempts"] = user1.get("connection_attempts", 0) + 1
            user2["connection_attempts"] = user2.get("connection_attempts", 0) + 1

            print(f"Creating room for {user1['name']} and {user2['name']}...")
            self.room_manager.create_room(user1, user2)

    def cleanup_inactive_users(self):
        """Remove users who have been inactive for too long"""
        current_time = time.time()
        with self.lock:
            inactive_users = []
            for socket_id, user in self.users.items():
                if current_time - user.get("last_activity", 0) > self.user_timeout:
                    inactive_users.append(socket_id)
            
            for socket_id in inactive_users:
                self.remove_user(socket_id)
                print(f"Removed inactive user {socket_id}")

    def update_user_activity(self, socket_id):
        """Update user's last activity timestamp"""
        if socket_id in self.users:
            self.users[socket_id]["last_activity"] = time.time()

    def get_user_by_socket(self, socket_id):
        """
        Get user information by socket ID.
        """
        return self.users.get(socket_id)

    def is_user_in_queue(self, socket_id):
        """
        Check if a user is currently in the queue.
        """
        return socket_id in self.queue and socket_id in self.users and self.users[socket_id].get("state") == "queue"

    def is_user_in_room(self, socket_id):
        """
        Check if a user is currently in a room.
        """
        return socket_id in self.users and self.users[socket_id].get("state") == "room"

    def get_queue_status(self):
        """
        Get current queue status for debugging.
        """
        with self.lock:
            return {
                "queue_length": len(self.queue),
                "queue_users": self.queue.copy(),
                "total_users": len(self.users),
                "user_states": {socket_id: user.get("state", "unknown") for socket_id, user in self.users.items()},
                "max_concurrent_users": self.max_concurrent_users,
                "active_rooms": self.room_manager.get_room_count()
            }
